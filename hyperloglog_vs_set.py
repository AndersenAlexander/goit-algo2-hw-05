import re
import time
import mmh3
import sys
from typing import Set
from rich.console import Console
from rich.table import Table


class HyperLogLog:
    """HyperLogLog implementation for approximate counting of unique elements."""

    def __init__(self, b: int = 12):
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m

    def add(self, item: str):
        # Obtain a 128-bit hash value as bytes
        hash_value = mmh3.hash_bytes(item)
        # Index into registers
        idx = int.from_bytes(hash_value[:4], "big") % self.m
        # Remaining bits used for rho calculation
        w = int.from_bytes(hash_value[4:], "big")
        self.registers[idx] = max(self.registers[idx], self._rho(w))

    def count(self) -> int:
        """Estimate the number of unique elements."""
        Z = sum(2 ** -r for r in self.registers)
        alpha_m = 0.7213 / (1 + 1.079 / self.m)
        estimate = alpha_m * (self.m ** 2) / Z
        return int(estimate)

    @staticmethod
    def _rho(w: int) -> int:
        """Find the position of the first 1-bit (method used in this implementation)."""
        return (w & -w).bit_length()


def load_ip_addresses(filename: str) -> Set[str]:
    """Load IP addresses from a log file."""
    ip_set: Set[str] = set()
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = ip_pattern.search(line)
            if match:
                ip_set.add(match.group())

    return ip_set


def benchmark(filename: str):
    """Compare exact counting vs. HyperLogLog."""
    console = Console()

    # Exact count
    start_time = time.time()
    exact_ips = load_ip_addresses(filename)
    exact_count = len(exact_ips)
    exact_time = time.time() - start_time

    # HyperLogLog estimate
    hll = HyperLogLog()
    start_time = time.time()
    for ip in exact_ips:
        hll.add(ip)
    hll_count = hll.count()
    hll_time = time.time() - start_time

    # Output results
    table = Table(
        title="Comparison Results", show_header=True, header_style="bold magenta"
    )
    table.add_column("", justify="left")
    table.add_column("Exact Counting", justify="right")
    table.add_column("HyperLogLog", justify="right")

    table.add_row("Unique elements", f"{exact_count:,}", f"{hll_count:,}")
    table.add_row("Execution time (s)", f"{exact_time:.5f}", f"{hll_time:.5f}")

    console.print(table)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a path to the log file.")
        sys.exit(1)

    benchmark(sys.argv[1])
