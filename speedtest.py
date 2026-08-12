import argparse

import requests
import time
from datetime import datetime
from argparse import ArgumentParser


REQUESTS_NUMBER = 10
TIMEOUT = 10
BYTES_IN_MEGABYTE = 1_000_000
CHUNK_SIZE = 8192


def parse_url() -> str:
    """
    Parse URL from command line arguments.

    :return: URL string
    """
    parser = ArgumentParser(
        description="Измеритель скорости загрузки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example:\n  python speedtest.py https://example.com/image.jpg'
    )
    parser.add_argument(
        'url',
        help='Ссылка на изображение для загрузки'
    )

    return parser.parse_args().url


def print_request_result(request_num: int, content_size: int, duration: float) -> None:
    """
    Print result of a single image download

    :param request_num: Current request number
    :param content_size: Size of request content
    :param duration: Request duration
    :return: None
    """
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} | INFO "
          f"| Загрузка {request_num}/{REQUESTS_NUMBER} завершена: "
          f"{duration:.3f} сек., {content_size} байт")


def print_final_result(avg_request_time: float, total_size_mb: float, average_speed: float) -> None:
    """
    Print final speed test result

    :param avg_request_time: Average request time in seconds
    :param total_size_mb: Total megabytes downloaded
    :param average_speed: Average download speed in MB/s
    :return: None
    """
    print()
    print("Итоги:")
    print(f"Среднее время запроса: {avg_request_time:.3f} сек.")
    print(f"Объём скачанных данных: {total_size_mb:.3f} МБ")
    print(f"Средняя скорость: {average_speed:.3f} МБ/с")


def download_image(session: requests.Session, url: str) -> tuple[float, int]:
    """
    Download image and measure download time and content size

    :param session: Session for pooling
    :param url: Image URL to download
    :return: Tuple of duration and content_size
    """
    start_time = time.perf_counter()

    response = session.get(url, stream=True, timeout=TIMEOUT)
    response.raise_for_status()

    content_size = 0
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            content_size += len(chunk)

    end_time = time.perf_counter()
    duration = end_time - start_time

    return duration, content_size


def speed_test(url: str) -> tuple[float, float, float]:
    """
    Run speed test

    :param url: Image URL
    :return: Tuple of avg_request_time, total_size_mb, average_speed
    """
    total_size_bytes = 0
    total_time = 0

    with requests.Session() as session:
        for i in range(1, REQUESTS_NUMBER + 1):
            try:
                duration, content_size = download_image(session, url)
            except requests.exceptions.RequestException as ex:
                print(f"При выполнении запроса произошла ошибка: {ex}")
                exit(1)
            except Exception as ex:
                print(f"Произошла неожиданная ошибка: {ex}")
                exit(1)

            total_size_bytes += content_size
            total_time += duration

            print_request_result(i, content_size, duration)

    avg_request_time = total_time / REQUESTS_NUMBER
    total_size_mb = total_size_bytes / BYTES_IN_MEGABYTE
    average_speed = total_size_mb / total_time

    return avg_request_time, total_size_mb, average_speed


def main():
    """
    Main function.
    """
    url = parse_url()
    avg_request_time, total_size_mb, average_speed = speed_test(url)
    print_final_result(avg_request_time, total_size_mb, average_speed)


if __name__ == '__main__':
    main()