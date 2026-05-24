import sys
import time
from typing import Iterator, Optional, Callable


def typewriter_print(
    text: str,
    min_speed: float = 0.01,
    max_speed: float = 0.4,
    target_duration: float = 3.0,
    output_func: Optional[Callable[[str], None]] = None,
) -> float:
    length = len(text)
    if length == 0:
        return 0.1
    
    base_speed = target_duration / length
    char_delay = max(min_speed, min(max_speed, base_speed))
    
    write = output_func or (lambda c: sys.stdout.write(c))
    
    for char in text:
        write(char)
        if not output_func:
            sys.stdout.flush()
        time.sleep(char_delay)
    
    if not output_func:
        print()
    
    return char_delay


def stream_print(
    text_iterator: Iterator[str],
    char_delay: float = 0.02,
    output_func: Optional[Callable[[str], None]] = None,
) -> str:
    write = output_func or (lambda c: sys.stdout.write(c))
    full_text = []
    
    for chunk in text_iterator:
        for char in chunk:
            write(char)
            full_text.append(char)
            if not output_func:
                sys.stdout.flush()
            if char_delay > 0:
                time.sleep(char_delay)
    
    if not output_func:
        print()
    
    return ''.join(full_text)


def stream_print_no_delay(
    text_iterator: Iterator[str],
    output_func: Optional[Callable[[str], None]] = None,
) -> str:
    return stream_print(text_iterator, char_delay=0.0, output_func=output_func)
