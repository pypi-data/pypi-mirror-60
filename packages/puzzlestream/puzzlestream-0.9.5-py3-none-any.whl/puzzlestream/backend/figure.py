import matplotlib
import matplotlib.pyplot as plt
import pickle


class PSFigure():

    def __init__(self, *args, **kwargs):

        if len(args) > 2:
            # Too many arguments
            try:
                Ex = ValueError()
                Ex.strerror = "Invalid number of arguments.\n" + \
                    "\t PSFigure(" + \
                    "figure: matplotlib.figure.Figure, savePath: str" +\
                    ") to save\n" +\
                    "\t PSFigure(loadPath: str) to load\n"

                raise Ex
            except ValueError as e:
                print("Value Error:", e.strerror)

        elif (
            len(args) == 2 and
            isinstance(args[0], matplotlib.figure.Figure) and
            isinstance(args[1], str)
        ):
            # Save mode initialiser
            self.__initSaveMode(args[0], args[1])

        elif (
            len(args) == 1 and
            isinstance(args[0], str)
        ):
            # Load mode initialiser
            self.__initLoadMode(args[0])

    def __initSaveMode(self, figure: matplotlib.figure.Figure, savePath: str):

        self.__mplVersion = matplotlib.__version__
        self.__figureHandle = figure
        self.write(savePath)

    def __initLoadMode(self, savePath: str):
        try:
            fCDict = pickle.load(
                open(savePath, 'rb')
            )
        except:
            try:
                Ex = ValueError()
                Ex.strerror = "Invalid argument.\n" + \
                    "There is no PSFigure saved in " + savePath + \
                    " or you do not have permission to read the file.\n"
                raise Ex
            except ValueError as e:
                print("Value Error:", e.strerror)

        self.__mplVersion = fCDict["mplVersion"]

        if self.__mplVersion != matplotlib.__version__:
            print(
                "WARNING: Current matplotlib version (" +
                str(matplotlib.__version__) +
                ") is different from the version" +
                " the Figure has been created with (" +
                str(self.__mplVersion) + "). " +
                "You may want to downgrade matplotlib or recreate the figures."
            )

        self.__figureHandle = fCDict["figureHandle"]

    def write(self, savePath: str):

        try:
            pickle.dump(
                {
                    "figureHandle": self.__figureHandle,
                    "mplVersion": self.__mplVersion
                },
                open(
                    savePath,
                    "wb"
                )
            )
        except:
            try:
                Ex = ValueError()
                Ex.strerror = "Invalid argument.\n" + \
                    "The PSFigure can not be saved in " + savePath + \
                    " as it is not a valid path or you do not" + \
                    " have permission to writing permission there.\n"
                raise Ex
            except ValueError as e:
                print("Value Error:", e.strerror)

    def getHandle(self):
        return self.__figureHandle
