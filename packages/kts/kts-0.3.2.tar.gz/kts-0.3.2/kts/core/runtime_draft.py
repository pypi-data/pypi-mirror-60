import time
from abc import ABC
from contextlib import contextmanager
import warnings

class Applier(ParallelFeatureConstructor):
    cache = False

    def __init__(self, func, parts=None, optimize=True):
        self.func = func
        if parts is None:
            parts = cfg.threads
        self.parts = parts
        self.optimize = optimize

    def map(self, df):
        if len(df) < 100 and self.optimize:
            yield (0, len(df))
        else:
            for part in range(self.parts):
                yield (part * len(df) // self.parts, (part + 1) * len(df) // self.parts)

    def compute(self, start, stop, df):
        return df.iloc[start:stop].apply(self.func, axis=1)

    def get_scope(self, start, stop):
        return f"stl_apply_{start}_{stop}"

    def reduce(self, results):
        return pd.concat(results, axis=0)


class CategoryEncoder(ParallelFeatureConstructor):
    def __init__(self, encoder, columns: Union[List[str], str], targets: Optional[Union[List[str], str]] = None):
        self.encoder = encoder
        if not isinstance(columns, list):
            columns = [columns]
        self.columns = columns
        if not isinstance(targets, list):
            targets = [targets]
        self.targets = targets
    
    def map(self, df):
        for col in self.columns:
            for tar in self.targets:
                yield (col, tar)

    def compute(self, col, tar, df):
        EncoderClass = self.encoder.__class__
        if df._train:
            params = self.encoder.get_params()
            params['cols'] = [col]
            enc = EncoderClass(**params)
            res = enc.fit_transform(df[[col]], df[tar])
            df._state['enc'] = enc
        else:
            enc = df._state['enc']
            res = enc.transform(df[[col]])
        col_name = f"{col}_ce_"
        if tar is not None:
            col_name += f"{tar}_"
        enc_params = enc.get_params()
        default_params = EncoderClass().get_params()
        diff = {k: v for k, v in enc_params.items() if enc_params[k] != default_params[k] and k != 'cols'}
        col_name += f"{EncoderClass.__name__}"
        if len(diff) > 0:
            col_name += "_" + "_".join(f"{k}.{v}" for k, v in diff.items())
        res.columns = [col_name]
        return res

    def get_scope(self, col, tar):
        return f"stl_category_encoder_{col}_{tar}"

    def reduce(self, results):
        return pd.concat(results, axis=1)


class Identity(InlineFeatureConstructor):
    def __init__(self):
        pass

    def compute(self, kf: KTSFrame, ret=True):
        if ret:
            return kf

    def get_alias(self, kf: KTSFrame):
        frame_cache = kf.__meta__['frame_cache']
        alias_name = frame_cache.save(kf)
        return frame_cache.load(alias_name, ret_alias=True)


class EmptyLike(InlineFeatureConstructor):
    def __init__(self):
        pass

    def compute(self, kf: KTSFrame, ret=True):
        if ret:
            return kf[[]]

    def get_alias(self, kf: KTSFrame):
        frame_cache = kf.__meta__['frame_cache']
        alias_name = frame_cache.save(kf[[]])
        return frame_cache.load(alias_name, ret_alias=True)


class Selector(InlineFeatureConstructor):
    def __init__(self, feature_constructor, columns):
        self.feature_constructor = feature_constructor
        self.columns = columns

    def compute(self, kf: KTSFrame, ret=True):
        res = self.feature_constructor.compute(kf)
        if ret:
            return res[[self.columns]]

    def get_alias(self, kf: KTSFrame):
        alias = self.feature_constructor.get_alias(kf)
        alias = alias & self.columns
        return alias

    @property
    def cache(self):
        return self.feature_constructor.cache

    @property
    def parallel(self):
        return self.feature_constructor.parallel
    


class Dropper(InlineFeatureConstructor):
    def __init__(self, feature_constructor, columns):
        self.feature_constructor = feature_constructor
        self.columns = columns

    def compute(self, kf: KTSFrame, ret=True):
        res = self.feature_constructor.compute(kf)
        if ret:
            return res.drop(self.columns, axis=1)

    def get_alias(self, kf: KTSFrame):
        alias = self.feature_constructor.get_alias(kf)
        alias = alias - self.columns
        return alias

    @property
    def cache(self):
        return self.feature_constructor.cache

    @property
    def parallel(self):
        return self.feature_constructor.parallel


class Concat(InlineFeatureConstructor):
    def __init__(self, feature_constructors):
        self.feature_constructors = feature_constructors

    def compute(self, kf: KTSFrame, ret=True):
        parallels = [f for f in self.feature_constructors if f.parallel]
        not_parallels = [f for f in self.feature_constructors if not f.parallel]
        results = dict()
        if len(parallels) > 0:
            interim = list()
            for f in parallels:
                interim.append(f.get_futures())
            for f, (scheduled, results) in zip(parallels, interim):
                f.wait(scheduled)
            for f, (scheduled, results) in zip(parallels, interim):
                results[f.name] = f.assemble_futures(scheduled, results, kf)
        if len(not_parallels) > 0:
            for f in not_parallels:
                results[f.name] = f(kf)
        results_ordered = [results[f.name] for f in self.feature_constructors]
        return pd.concat(results_ordered, axis=1)

    def get_alias(self, kf: KTSFrame):
        aliases = [fc.get_alias(kf) for fc in self.feature_constructors]
        if all(isinstance(i, DataFrameAlias) for i in aliases):
            res = aliases[0]
            for alias in aliases[1:]:
                res = res.join(alias)
            return res
        else:
            frame_cache = df.__meta__['frame_cache']
            res = frame_cache.concat(aliases)
            return res




# ========= OLD ========


@ray.remote
class RemoteFeatureConstructor:
    def __init__(self, function):
        self.function = function
        self.name = function.__name__
        self.old_cache = dict()  # Dict[RunID, Tuple[AnyFrame, Dict]]
        self.new_cache = dict()  # Dict[RunID, Tuple[AnyFrame, Dict, Dict]]

    def request_cache(self, run_id: RunID) -> bool:
        rs.send(CacheRequest(run_id))
        while True:
            signals = rs.receive([response_sender], timeout=0.1)
            broadcast_cache_responses = filter_signals(signals, BroadcastCacheResponse)
            merged_cache_responses = sum([i.get_contents() for i in broadcast_cache_responses], [])
            responses = [i for i in merged_cache_responses if i['run_id'] == run_id]
            if len(responses) > 0:
                response = responses[0]
        content = response.get_contents()
        success = content['success']
        if success:
            self.old_cache[run_id] = ray.get(content['object_id'])
            return True
        else:
            return False

    def run(self, df: AnyFrame, meta: Dict, kwargs: Dict, ret=False) -> Optional[Tuple[AnyFrame, Dict]]:
        rs.send(Start())
        for key in kwargs:
            if isinstance(kwargs[key], ObjectID):
                kwargs[key] = ray.get(kwargs[key])
            elif isinstance(kwargs[key], str):
                self.request_dependency
        ktsframe = KTSFrame(df=df, meta=meta)
        ktsframe.__meta__['scope'] = self.name
        run_id = RunID(ktsframe.scope, ktsframe.fold, hash(ktsframe))
        old_run = self.old_cache.get(run_id, None)
        new_run = self.new_cache.get(run_id, None)
        res_run = old_run or new_run
        if res_run is not None:
            if ret:
                return res_run
            else:
                return
        if self.request_cache(run_id):
            return self.old_cache[run_id]
        stats = dict()
        stats['input_shape'] = ktsframe.shape
        tmp_stdout = sys.stdout
        sys.stdout = RemoteTextIO()
        start = time.time()
        res = self.func(ktsframe, **kwargs)
        sys.stdout = tmp_stdout
        stats['took'] = time.time() - start
        res_state = ktsframe.state
        self.new_cache[run_id] = (res, res_state, stats)
        rs.send(Finish())
        if ret:
            return res, res_state

    def get_new(self) -> Dict[RunID, Tuple[AnyFrame, Dict]]:
        return self.new_cache


class EphemericRemoteFeatureConstructor:
    def __init__(self, function):
        self.function = function
        self.name = function.__name__
        self.result = None
        self.state = None

    def run(self, df: AnyFrame, meta: Dict) -> None:
        ktsframe = KTSFrame(df=df, meta=meta)
        ktsframe.__meta__['scope'] = self.name
        self.result = self.function(ktsframe)
        self.state = self.result.state
        rs.send(Finish())

    def get_result(self) -> AnyFrame:
        return self.result

    def get_state(self) -> Any:
        return self.state


class STLFeatureConstructor(ABC):
    parallel = True
    computable = True
    cache = True

    def __call__(self, df: KTSFrame) -> KTSFrame:
        if df.__meta__['remote'] and self.parallel:
            pass
        else:
            pass

    # def wait(self):
    #     pass

    # def check(self):
    #     pass

    # def collect(self):
    #     pass

    @abstractmethod
    def map(self, kf: KTSFrame) -> List[Tuple]:
        raise NotImplemented

    @abstractmethod
    def compute(self, *args) -> KTSFrame:
        raise NotImplemented

    @abstractmethod
    def reduce(self, results: List[KTSFrame/pd.DataFrame]) -> KTSFrame:
        raise NotImplemented


class CategoryEncode(STLFeatureConstructor):
    parallel = True
    computable = True
    cache = True

    def __init__(self, encoder: Any, columns: List[str], targets: List[str]):
        self.encoder = encoder
        self.columns = columns
        self.targets = targets

    def map(self, kf: KTSFrame):
        payload = []
        for col in self.columns:
            for tg in self.targets:
                payload.append((col, tg))
        return payload

    def compute(self, column: str, target: str, kf: KTSFrame) -> KTSFrame:
        if kf.train:
            enc = copy(self.encoder)
            enc.fit(kf[[column]], kf[[target]])
            kf.state = enc
        else:
            enc = kf.state
        enc.transform()


class OneHotEncode(STLFeatureConstructor):
    parallel = False
    computable = True
    cache = False

    def __init__(self, encoder: Any, columns: List[str], targets: List[str]):
        self.encoder = encoder
        self.columns = columns
        self.targets = targets

    def map(self, kf: KTSFrame):
        payload = []
        for col in self.columns:
            for tg in self.targets:
                payload.append((col, tg))
        return payload

    def compute(self, column: str, target: str, kf: KTSFrame) -> KTSFrame:
        if kf.train:
            enc = copy(self.encoder)
            enc.fit(kf[[column]], kf[[target]])
            kf.state = enc
        else:
            enc = kf.state
        enc.transform()

class Identity(STLFeatureConstructor):
    parallel = False
    computable = False
    cache = False

    def __init__(self, encoder: Any, columns: List[str], targets: List[str]):
        self.encoder = encoder
        self.columns = columns
        self.targets = targets

    def map(self, kf: KTSFrame):
        payload = []
        for col in self.columns:
            for tg in self.targets:
                payload.append((col, tg))
        return payload

    def compute(self, column: str, target: str, kf: KTSFrame) -> KTSFrame:
        if kf.train:
            enc = copy(self.encoder)
            enc.fit(kf[[column]], kf[[target]])
            kf.state = enc
        else:
            enc = kf.state
        enc.transform()

class EmptyLike(STLFeatureConstructor):
    parallel = False
    computable = False
    cache = False

    def __init__(self, encoder: Any, columns: List[str], targets: List[str]):
        self.encoder = encoder
        self.columns = columns
        self.targets = targets

    def map(self, kf: KTSFrame):
        payload = []
        for col in self.columns:
            for tg in self.targets:
                payload.append((col, tg))
        return payload

    def compute(self, column: str, target: str, kf: KTSFrame) -> KTSFrame:
        if kf.train:
            enc = copy(self.encoder)
            enc.fit(kf[[column]], kf[[target]])
            kf.state = enc
        else:
            enc = kf.state
        enc.transform()


class FeatureConstructor(HTMLRepr):
    def __init__(self, function, dependencies: Dict[str, str] = None):
        self.function = function
        self.name = function.__name__
        self.select = []
        self.drop = []
        self.parallel = True
        self.cache = True
        self.dependencies = dependencies

    @property
    def actor(self):
        return global_actors[self.name]

    def __call__(self, df: KTSFrame) -> KTSFrame:
        df = df
        meta = df.__meta__
        res_df, res_state = self.actor.remote(df, meta, self.dependencies, ret=True)
        res = KTSFrame(res_df, res_meta)
        return res[self.select]  # fix

    def __sub__(self, cols):
        pass

    def __and__(self, cols):
        pass

    def _html_elements(self):
        elements = [
            Annotation('name'),
            Field(self.name),
            Annotation('source'),
            Code(self.source),
            Annotation('columns'),
            Field('[' + ', '.join(self.columns) + ']')
        ]
        if self.preview_df is not None:
            elements += [Annotation('preview'), DF(self.preview_df)]
        return elements
    
    @property
    def html(self):
        elements = [Title('feature constructor')]
        elements += self._html_elements()
        return Column(elements).html
    
    @property
    def html_collapsible(self):
        cssid = np.random.randint(1000000000)
        elements = [TitleWithCross('feature constructor', cssid)]
        elements += self._html_elements()
        return CollapsibleColumn(elements, ThumbnailField(self.name, cssid), cssid).html



# class RunManager:
#     def __init__(self):
#         self.runs = CachedMapping('runs')  # Dict[RunID, Run]
#         self.states = CachedMapping('states')

#     def submit_batch(self, feature_constructors: List[FeatureConstructor], frame: KTSFrame):
#         assert all(fc.parallel for fc in feature_constructors)
#         actors = [fc.actor for fc in feature_constructors]
#         frame_id = ray.put(frame)
#         meta = frame.__meta__
#         for actor in actors:
#             actor.remote.run()

#     def supervise(self, report=None):

#     # def run_sequentially(self, feature_constructors: List[FeatureConstructor], frame: KTSFrame, report=None):
#     #     pbar = LocalProgressBar
#     #     pbar.report = report
#     #     for fc in feature_constructors:
#     #         frame.__meta__['scope'] = fc.name
#     #         run_id = RunID(frame.scope, frame.fold, hash(frame))
#     #         pbar.run_id = run_id
#     #         report.start(run_id)

#     #         stats = dict()
#     #         stats['input_shape'] = ktsframe.shape
#     #         sys.stdout = LocalTextIO()
#     #         start = time.time()
#     #         res = self.func(ktsframe, **kwargs)
#     #         sys.stdout = cfg.builtin_stdout
#     #         stats['took'] = time.time() - start

#     #         report.finish(run_id)

#     #         res_df = res
#     #         res_state = res.state
#     #         if fc.cache:
#     #             frame_cache.save_run(df=res_df, run_id=run_id)
#     #             obj_cache.save(res_state, run_id.get_state_name())
#     #             run = Run(run_id.get_alias_name(), run_id.get_state_name(), stats)
#     #         else:
#     #             ???
#     #     pbar = RemoteProgressBar

#     def sync(self):
#         for actor in global_actors:
#             new_cache = ray.get(actor.get_new.remote())
#             actor.clear_cache.remote()
#             for run_id in new_cache:
#                 res_df, res_state, stats = new_runs[run_id]
#                 if @DO_CACHE:
#                     frame_cache.save_run(df=res_df, run_id=run_id)
#                     obj_cache.save(res_state, run_id.get_state_name())
#                     run = Run(run_id.get_alias_name(), run_id.get_state_name(), stats)
#                     self.runs[run_id] = run
#                 else:



# class Run:
#     def __init__(self, result_frame_name: str, state_diff_name: str, stats: Dict[str, int]):
#         self.result_frame_name = result_frame_name
#         self.state_diff_name = state_diff_name
#         self.stats = copy(stats)

#     @property
#     def result(self) -> DataFrameAlias:
#         return frame_cache.load_run(self.result_frame_name)

#     @property
#     def state(self) -> Dict:
#         return obj_cache.load(self.state_diff_name)

