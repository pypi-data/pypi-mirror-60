import time

def SimpleBar(progress, long=20, char_done='=', char_undone='.', arrow='>', **kwargs):
    show_percent = kwargs.get('show_percent')
    num = int(progress * long)
    bar = char_done * (num - 1) + arrow + char_undone * (long - num)
    bar += '({percent}%)'.format(percent=str(progress * 100.)[:5])
    # if show_percent is not None and show_percent == True:
    return bar

if __name__ == '__main__':
    print((SimpleBar(0, show_percent=True)))