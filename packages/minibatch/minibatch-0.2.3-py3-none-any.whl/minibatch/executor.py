class SerialExecutor:
    def exec(self, fn, args):
        return fn(args)


class ParallelExecutor:
