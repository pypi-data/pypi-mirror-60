import math
import numpy as np

def dist(point, start, end):
    if np.all(np.equal(start, end)):
        return np.linalg.norm(point - start)

    return np.divide(
            np.abs(np.linalg.norm(np.cross(end - start, start - point))),
            np.linalg.norm(end - start))


def rdp(pts, leave: int):
    weights = []
    length = len(pts)

    # def rdp_rec(start, end):
    #     if (end > start + 1):
    #         line = Line(points[start], points[end])
    #         maxDist = -1
    #         maxDistIndex = 0

    #         for i in range(start + 1, end):
    #             dist = line.distanceToSquared(points[i])
    #             if dist > maxDist:
    #                 maxDist = dist
    #                 maxDistIndex = i

    #         weights.insert(maxDistIndex, maxDist)

    #         rdp_rec(start, maxDistIndex)
    #         rdp_rec(maxDistIndex, end)

    pts = np.array(pts)

    weights = []

    def rdp_rec(M):
        if M.shape[0] < 3:
            return
        dmax = -1
        index = 0

        for i in range(1, M.shape[0]):
            d = dist(M[i], M[0], M[-1])

            if d > dmax:
                index = i
                dmax = d

        weights.insert(index, dmax)

        rdp_rec(M[:index + 1])
        rdp_rec(M[index:])


    rdp_rec(pts)

    weights.insert(0, np.inf)
    weights.append(np.inf)

    max_tolerance = np.partition(weights, len(pts) - leave)[len(pts) - leave]
    res = [p for i, p in enumerate(pts) if weights[i] >= max_tolerance]

    return result