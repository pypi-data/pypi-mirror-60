#!/usr/bin/env python3
from hashlib import sha1
import os
from binascii import hexlify

SHA1_HASH_SIZE = 20

class PasswordDB:
    # Each record is 0x18 bytes:
    #   0x00-0x13: hash
    #   0x14-0x17: count
    RECORD_SIZE = SHA1_HASH_SIZE + 4

    def __init__(self, f):
        self.f = f              # for writing
        self.fd = f.fileno()    # for preading
        self.mode = f.mode.replace('b', '')
        if not self.mode in ('r', 'w'):
            raise ValueError("mode must be r or w")
        self._last_added_hash = None

    @classmethod
    def open(cls, path, mode='r'):
        f = open(path, mode+'b')
        return cls(f)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def close(self):
        self.f.close()
        self.fd = -1

    def add_hash(self, h, count=0):
        """Add a hash to the password db

        NOTE: Assumes the hashes are added in sorted order!
        """
        if self.mode != 'w':
            raise RuntimeError("Database not writable")

        if len(h) != SHA1_HASH_SIZE:
            raise ValueError("Invalid hash size")

        # Try to ensure sorted order as required by binary search algorithm
        if self._last_added_hash and h < self._last_added_hash:
            raise ValueError("add_hash() must be called with hashes in order")
        self._last_added_hash = h

        self.f.write(h)
        self.f.write(count.to_bytes(4, 'little'))


    def search_password(self, pw):
        # "Each password is stored as a SHA-1 hash of a UTF-8 encoded password."
        h = sha1(pw.encode('UTF-8'))
        return self._binsearch(h.digest())


    def _read_nth(self, n):
        off = n * self.RECORD_SIZE
        data = os.pread(self.fd, self.RECORD_SIZE, off)
        if len(data) != self.RECORD_SIZE:
            raise IOError("pread returned 0x{:X}/0x{:X} bytes".format(len(data), self.RECORD_SIZE))

        hash_bin = data[0:SHA1_HASH_SIZE]
        count = int.from_bytes(data[SHA1_HASH_SIZE : SHA1_HASH_SIZE+4], 'little')

        return hash_bin, count


    def _binsearch(self, h):
        if self.mode != 'r':
            raise RuntimeError("Database not readable")

        assert len(h) == SHA1_HASH_SIZE

        filesize = os.fstat(self.fd).st_size
        assert (filesize % self.RECORD_SIZE) == 0
        nrec = filesize // self.RECORD_SIZE

        # The indicies of the record in current range of search
        idx_start = 0       # first @ start of range
        idx_end = nrec      # first after end of range

        while idx_start != idx_end:
            # Calculate an approximate midpoint
            mid = ((idx_end - idx_start) // 2) + idx_start 

            cur_hash, cur_count = self._read_nth(mid)

            if h == cur_hash:
                return cur_count
            elif h < cur_hash:
                # Search the bottom half
                idx_end = mid
            else:
                # Search the top half
                idx_start = mid + 1

        raise KeyError("Hash not found")
            

if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('file', type=argparse.FileType('r'),
            help="Passdb file to search")
    ap.add_argument('password', nargs='+',
            help="Passwords for which to search")

    args = ap.parse_args()


    db = PasswordDB(args.file)

    for pw in args.password:
        try:
            count = db.search_password(pw)
        except KeyError:
            print("{}: Not found in DB".format(pw))
            continue

        print("{}: {}".format(pw, count))
