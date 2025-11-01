from bitarray import bitarray
import mmh3
from colorama import Fore, Style, init
from typing import List, Dict

init(autoreset=True)


class BloomFilter:
    """
    Simple Bloom filter implementation using murmurhash3 (mmh3) and bitarray.

    Note: Bloom filters can produce false positives (reporting an item is present when it is not),
    but never false negatives (if properly used).
    """

    def __init__(self, size: int, num_hashes: int):
        """
        :param size: Number of bits in the filter.
        :param num_hashes: Number of hash functions to apply per item.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def _indexes(self, item: str):
        """Generate bit indexes for the given item."""
        for i in range(self.num_hashes):
            # mmh3.hash can return negatives; modulo handles that fine in Python
            yield mmh3.hash(item, i) % self.size

    def add(self, item: str) -> None:
        """Add an item to the Bloom filter."""
        for index in self._indexes(item):
            self.bit_array[index] = 1

    def contains(self, item: str) -> bool:
        """Return True if the item may be in the set (False means definitely not)."""
        return all(self.bit_array[index] for index in self._indexes(item))

    # Pythonic alias to support: `item in bloom`
    def __contains__(self, item: str) -> bool:
        return self.contains(item)


def check_password_uniqueness(bloom: BloomFilter, passwords: List[str]) -> Dict[str, str]:
    """
    Check each password against the Bloom filter and return a dict mapping password -> status string.
    """
    results: Dict[str, str] = {}
    for password in passwords:
        if bloom.contains(password):
            results[password] = f"{Fore.RED}possibly already used{Style.RESET_ALL}"
        else:
            results[password] = f"{Fore.GREEN}unique (not seen){Style.RESET_ALL}"
    return results


if __name__ == "__main__":
    # Example usage
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Existing passwords (insert into the filter)
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for pwd in existing_passwords:
        bloom.add(pwd)

    # New passwords to check
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    print("\nPassword check results:")
    for password, status in results.items():
        print(f"{Fore.CYAN}Password '{password}' — {status}.")
