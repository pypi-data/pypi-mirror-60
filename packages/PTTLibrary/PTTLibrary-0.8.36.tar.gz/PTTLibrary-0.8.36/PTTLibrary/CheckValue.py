
try:
    from . import i18n
    from . import Log
    from . import Util
except ModuleNotFoundError:
    import i18n
    import Log
    import Util


def check(
    Config,
    Type,
    Name,
    Value,
    Class=None
):

    if not isinstance(Value, Type):
        if Type is str:
            raise TypeError(
                Log.merge(
                    Config,
                    [
                        Name,
                        i18n.MustBe,
                        i18n.String
                    ]))
        elif Type is int:
            raise TypeError(
                Log.merge(
                    Config,
                    [
                        Name,
                        i18n.MustBe,
                        i18n.Integer
                    ]))
        elif Type is bool:
            raise TypeError(
                Log.merge(
                    Config,
                    [
                        Name,
                        i18n.MustBe,
                        i18n.Boolean
                    ]))

    if Class is not None:
        if not Util.checkRange(Class, Value):
            raise ValueError(f'Unknow {Name}', Value)


def checkIndex(
    Config,
    IndexName,
    Index,
    MaxValue=None
):
    check(Config, int, IndexName, Index)
    if Index < 1:
        raise ValueError(
            Log.merge(
                Config,
                [
                    IndexName,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if MaxValue is not None:
        if Index > MaxValue:
            Log.showValue(
                Config,
                Log.Level.INFO,
                'Index',
                Index
            )
            Log.showValue(
                Config,
                Log.Level.INFO,
                'MaxValue',
                MaxValue
            )
            raise ValueError(
                Log.merge(
                    Config,
                    [
                        IndexName,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))


def checkIndexRange(
    Config,
    StartName,
    StartIndex,
    EndName,
    EndIndex,
    MaxValue=None
):

    check(Config, int, StartName, StartIndex)
    check(Config, int, EndName, EndIndex)

    if StartIndex < 1:
        raise ValueError(
            Log.merge(
                Config,
                [
                    StartName,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if StartIndex < 1:
        raise ValueError(
            Log.merge(
                Config,
                [
                    StartName,
                    i18n.ErrorParameter,
                    i18n.OutOfRange,
                ]))

    if StartIndex > EndIndex:
        raise ValueError(
            Log.merge(
                Config,
                [
                    StartName,
                    i18n.MustSmallOrEqual,
                    EndName,
                ]))

    if MaxValue is not None:
        if StartIndex > MaxValue:
            raise ValueError(
                Log.merge(
                    Config,
                    [
                        StartName,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))

        if EndIndex > MaxValue:
            raise ValueError(
                Log.merge(
                    Config,
                    [
                        EndName,
                        i18n.ErrorParameter,
                        i18n.OutOfRange,
                    ]))


if __name__ == '__main__':
    QQ = str

    if QQ is str:
        print('1')

    if QQ == str:
        print('2')

    if isinstance('', QQ):
        print('3')
