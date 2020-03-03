#!/usr/bin/env python3

import arkouda as ak

def pretest(N):
    """To trigger the gather bug, it seems to be necessary to read/generate a large array of strings, possibly slice it, and hash it. It might have something to do with the fact that the string bytes are uint8 and not necessarily word-aligned. The slice and hash are both moving this potentially non-aligned data over the network."""
    s = ak.random_strings_uniform(1, 20, 2*N)
    ss = s[:N]
    h = ss.hash()
    return h

def test(inputSize, outputSize, trials):
    """This test sometimes triggers the bug. It performs the same gather operation on bools repeatedly and tests whether the results are identical. Values are drawn randomly, with replacement."""
    bag = ak.randint(0, 2, inputSize, dtype=ak.bool)
    inds = ak.randint(0, inputSize, outputSize, dtype=ak.int64)
    res = []
    t1 = bag[inds]
    for trial in range(trials):
        t2 = bag[inds]
        res.append((t1 == t2).all())
        t1 = t2
    return res

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-size', type=int, default=10**6)
    parser.add_argument('-o', '--output-size', type=int, default=10**7)
    parser.add_argument('-t', '--trials', type=int, default=10)
    parser.add_argument('hostname')
    parser.add_argument('port', type=int, default=5555)
    args = parser.parse_args()
    ak.connect(args.hostname, args.port)
    pretest(args.output_size)
    res = test(args.input_size, args.output_size, args.trials)
    nFail = len(res) - sum(res)
    if nFail == 0:
        print("Got expected result")
        sys.exit(0)
    else:
        print(f"{nFail} failures in {args.trials} trials ({nFail/args.trials:.2%} failure rate)")
        sys.exit(1)
