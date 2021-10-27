from osgeo import gdal
import numpy

# imagine a nodata value of 0
NODATA = 0
ARRAY = numpy.array([
    [0, 1, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1],
    [0, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 0],
    [1, 0, 1, 1, 1, 0]], dtype=numpy.uint8)

EXPECTED_HOLES = numpy.array([
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0]], dtype=numpy.uint8)

# row, col
NEIGHBOR_OFFSET = [
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1)
]


def detect(array, cardinal_dir_only=False):
    # Return an array of where the holes are located.
    out_array = numpy.full(array.shape, 255)  # 255 is nodata

    # Seed the queue with the edge pixels -- anything reachable from the edge
    # is not a hole.
    work_queue = []
    for row in range(array.shape[1]):
        if row in (0, array.shape[1]-1):
            col_range = range(array.shape[0])
        else:
            col_range = (0, array.shape[0]-1)

        for col in col_range:
            if array[col, row] == 0:
                work_queue.append((col, row))

    step = 1
    if cardinal_dir_only:
        step = 2

    for seed_col, seed_row in work_queue:
        out_array[seed_col, seed_row] = 0

        for i in range(0, 8, step):
            neighbor_row = seed_row + NEIGHBOR_OFFSET[i][0]
            neighbor_col = seed_col + NEIGHBOR_OFFSET[i][1]

            if neighbor_row < 0 or neighbor_row >= array.shape[1]:
                continue
            if neighbor_col < 0 or neighbor_col >= array.shape[0]:
                continue

            if (out_array[neighbor_col, neighbor_row] == 255 and
                    array[neighbor_col, neighbor_row] == 0):
                work_queue.append((neighbor_col, neighbor_row))

    print(out_array)

    # any nodata not reachable from the borders are holes
    out_array[(out_array == 255) & (array == 0)] = 1
    out_array[out_array == 0] = 255
    print(out_array)


if __name__ == '__main__':
    print('Including diagonals in search')
    detect(ARRAY)
    print('')
    print('Cardinal directions only in search')
    detect(ARRAY, True)
