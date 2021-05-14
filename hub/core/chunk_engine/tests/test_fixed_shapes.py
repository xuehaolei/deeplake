import pytest

import numpy as np

from hub.core.tests.common import parametrize_all_storages_and_caches, current_test_name  # type: ignore
from hub.core.chunk_engine.tests.common import (
    run_engine_test,
    benchmark_write,
    benchmark_read,
    CHUNK_SIZES,
    DTYPES,
    get_random_array,
)

from typing import Tuple
from hub.core.typing import StorageProvider


np.random.seed(1)


# number of batches (unbatched implicitly = 1 sample per batch) per test
NUM_BATCHES = (1,)


UNBATCHED_SHAPES = (
    (1,),
    (100,),
    (1, 1, 3),
    (20, 90),
    (3, 28, 24, 1),
)


BATCHED_SHAPES = (
    (1, 1),
    (10, 1),
    (1, 30, 30),
    (3, 3, 12, 12, 1),
)


# for benchmarks
BENCHMARK_NUM_BATCHES = (1,)
BENCHMARK_DTYPES = (
    "int64",
    "float64",
)
BENCHMARK_CHUNK_SIZES = (16000000,)  # 16MB
BENCHMARK_BATCHED_SHAPES = (
    # with int64/float64 = ~1GB
    (840, 224, 224, 3),
)


@pytest.mark.parametrize("shape", UNBATCHED_SHAPES)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZES)
@pytest.mark.parametrize("num_batches", NUM_BATCHES)
@pytest.mark.parametrize("dtype", DTYPES)
@parametrize_all_storages_and_caches
def test_unbatched(
    shape: Tuple[int],
    chunk_size: int,
    num_batches: int,
    dtype: str,
    storage: StorageProvider,
):
    """
    Samples have FIXED shapes (must have the same shapes).
    Samples are provided WITHOUT a batch axis.
    """

    arrays = [get_random_array(shape, dtype) for _ in range(num_batches)]
    run_engine_test(arrays, storage, batched=False, chunk_size=chunk_size)


@pytest.mark.parametrize("shape", BATCHED_SHAPES)
@pytest.mark.parametrize("chunk_size", CHUNK_SIZES)
@pytest.mark.parametrize("num_batches", NUM_BATCHES)
@pytest.mark.parametrize("dtype", DTYPES)
@parametrize_all_storages_and_caches
def test_batched(
    shape: Tuple[int],
    chunk_size: int,
    num_batches: int,
    dtype: str,
    storage: StorageProvider,
):
    """
    Samples have FIXED shapes (must have the same shapes).
    Samples are provided WITH a batch axis.
    """

    arrays = [get_random_array(shape, dtype) for _ in range(num_batches)]
    run_engine_test(arrays, storage, batched=True, chunk_size=chunk_size)


@pytest.mark.benchmark(group="write_array")
@pytest.mark.parametrize("shape", BENCHMARK_BATCHED_SHAPES)
@pytest.mark.parametrize("chunk_size", BENCHMARK_CHUNK_SIZES)
@pytest.mark.parametrize("num_batches", BENCHMARK_NUM_BATCHES)
@pytest.mark.parametrize("dtype", BENCHMARK_DTYPES)
@parametrize_all_storages_and_caches
def test_write(
    benchmark,
    shape: Tuple[int],
    chunk_size: int,
    num_batches: int,
    dtype: str,
    storage: StorageProvider,
):
    """
    Benchmark `write_array`.

    Samples have FIXED shapes (must have the same shapes).
    Samples are provided WITH a batch axis.
    """

    arrays = [get_random_array(shape, dtype) for _ in range(num_batches)]

    gbs = (np.prod(shape) * num_batches * np.dtype(dtype).itemsize) // (1_000_000_000)
    print("\nBenchmarking array with size: %.2fGB." % gbs)

    key = current_test_name(with_uuid=True)

    benchmark(
        benchmark_write,
        key,
        arrays,
        chunk_size,
        storage,
        batched=True,
    )


@pytest.mark.benchmark(group="read_array")
@pytest.mark.parametrize("shape", BENCHMARK_BATCHED_SHAPES)
@pytest.mark.parametrize("chunk_size", BENCHMARK_CHUNK_SIZES)
@pytest.mark.parametrize("num_batches", BENCHMARK_NUM_BATCHES)
@pytest.mark.parametrize("dtype", BENCHMARK_DTYPES)
@parametrize_all_storages_and_caches
def test_read(
    benchmark,
    shape: Tuple[int],
    chunk_size: int,
    num_batches: int,
    dtype: str,
    storage: StorageProvider,
):
    """
    Benchmark `read_array`.

    Samples have FIXED shapes (must have the same shapes).
    Samples are provided WITH a batch axis.
    """

    arrays = [get_random_array(shape, dtype) for _ in range(num_batches)]

    key = current_test_name(with_uuid=True)

    actual_key = benchmark_write(key, arrays, chunk_size, storage, batched=True)
    benchmark(benchmark_read, actual_key, storage)
