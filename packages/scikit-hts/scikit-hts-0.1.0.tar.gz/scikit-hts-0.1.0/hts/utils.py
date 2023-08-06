import numpy
import pandas


def partition_column(column, n=3):
    partitioned = column.apply(lambda x: numpy.random.dirichlet(numpy.ones(n),size=1).ravel() * x).values
    return [[i[j] for i in partitioned] for j in range(n)]


def hierarchical_sine_data(start, end, n=10000):
    dts = (end - start).total_seconds()
    dti = pandas.DatetimeIndex([start + pandas.Timedelta(numpy.random.uniform(0, dts), 's')
                                for _ in range(n)]).sort_values()
    time = numpy.arange(0, len(dti), 0.01)
    amplitude = numpy.sin(time) * 10
    amplitude += numpy.random.normal(2 * amplitude + 2, 5)
    df = pandas.DataFrame(index=dti, data={'total': amplitude[0:len(dti)]})
    df['a'], df['b'], df['c'] = partition_column(df.total, n=3)
    df['aa'], df['ab'] = partition_column(df.a, n=2)
    df['aaa'], df['aab'] = partition_column(df.aa, n=2)
    df['ba'], df['bb'], df['bc'] = partition_column(df.b, n=3)
    df['ca'], df['cb'], df['cc'], df['cd'] = partition_column(df.c, n=4)
    return df
