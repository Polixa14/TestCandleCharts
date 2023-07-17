import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from receiving_data import get_market_data, get_pdh_pdl


def main(ticker, interval, candle_range):
    # Always show all figures during test
    show_pd = True
    show_bearish_bos = True
    show_bullish_bos = True

    last_down = 0
    last_down_index = 0
    last_low = 0
    last_up_index = 0
    last_up_low = 0
    last_high = 0

    # Receiving data in pandas DF format
    data = get_market_data(ticker, interval)

    # Plot parametrize
    plt.rcParams['figure.figsize'] = (40, 30)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%D %H:%M:%S'))
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    # To draw all boxes to one line
    right_border = data.iloc[-1, 0] + datetime.timedelta(hours=1)

    # Draw PDH, PDL
    if show_pd:
        pdh, pdl = get_pdh_pdl(ticker)
        ax.axhline(y=pdh, color='blue', linestyle='-')
        ax.annotate('PDH', xy=(data.iloc[-1, 0], pdh * 1.00002), fontsize=20)
        ax.annotate('PDL', xy=(data.iloc[-1, 0], pdl * 1.00002), fontsize=20)
        ax.axhline(y=pdl, color='blue', linestyle='-')

    bullish_candle = False
    short_boxes = []
    long_boxes = []
    for index, candle in data.iterrows():
        bos_candle = False

        if index > 0:

            # Get bottom of structure(in candle range)
            structure_low = data.loc[index-candle_range:index-1, 'low'].min()
            structure_low_index = data.loc[
                                  index-candle_range:index-1, 'low'].idxmin()

            # Bearish break of structure
            if candle.low < structure_low:
                if index - last_up_index < 1000:

                    # Doesn't draw anything if it wasn't green candles yet
                    if last_up_low != 0:

                        # Delete duplicates
                        for i, short_box in enumerate(short_boxes):
                            if short_box.get_xy() == (data.time[last_up_index],
                                                      last_up_low):
                                short_boxes.pop(i)
                                short_box.remove()

                        # Add bearish order block
                        short_boxes.append(
                            ax.add_patch(Rectangle(
                                (data.time[last_up_index], last_up_low),
                                width=right_border-data.time[last_up_index],
                                height=last_high-last_up_low,
                                alpha=0.3,
                                color='red'))
                        )

                    # Ignore if low = previous candle
                    if data.time[structure_low_index] != data.iloc[index-1, 0]:

                        # Add bearish BOS line
                        if show_bearish_bos:
                            ax.hlines(structure_low,
                                      data.time[structure_low_index],
                                      candle.time,
                                      color='red')
                        bos_candle = True
                    bullish_candle = False

        # Looking for bullish BOS
        for i, short_box in enumerate(short_boxes):
            left, bottom = short_box.get_xy()
            top = bottom + short_box.get_height()

            # Remove short box if current candle break top of order block
            if candle.close > top:
                short_boxes.pop(i)
                short_box.remove()

                if index - last_down_index < 1000:
                    if last_low != 0:

                        # Add bullish order block
                        long_boxes.append(
                            ax.add_patch(Rectangle(
                                (data.time[last_down_index], last_low),
                                width=right_border-data.time[last_down_index],
                                height=last_down-last_low,
                                alpha=0.3,
                                color='green')))

                        # Ignore if high = previous candle
                        if left != data.iloc[index - 1, 0]:

                            # Add bullish BOS line
                            if show_bullish_bos:
                                ax.hlines(top,
                                          left,
                                          candle.time,
                                          color='green')
                            bos_candle = True
                    bullish_candle = True

        # Remove long box if current candle break bot of order block
        for i, long_box in enumerate(long_boxes):
            left, bottom = long_box.get_xy()
            if candle.close < bottom:
                long_boxes.pop(i)
                long_box.remove()

        # Paint candle border
        if candle.close >= candle.open:
            candle_border_color = 'green'
        else:
            candle_border_color = 'red'

        # Paint candle
        candle_color = 'green' if bullish_candle else 'red'
        candle_color = 'yellow' if bos_candle else candle_color

        # Add candle shadows
        ax.vlines(candle.time, candle.low, candle.high,
                  color=candle_border_color, linewidth=0.5)

        # Add candle borders
        ax.vlines(candle.time, candle.open, candle.close,
                  color=candle_border_color, linewidth=3)

        # Add candle fill
        ax.vlines(candle.time, candle.open, candle.close,
                  color=candle_color, linewidth=1.5)

        # Update last down and up candles
        if candle.close < candle.open:
            last_down = candle.high
            last_down_index = index
            last_low = candle.low
        elif candle.close > candle.open:
            last_up_index = index
            last_up_low = candle.low
            last_high = candle.high

        # Update last high and last low
        last_high = candle.high if candle.high > last_high else last_high
        last_low = candle.low if candle.low < last_low else last_low

    # Save and show result
    plt.savefig(f'results/{ticker}-{interval}.png')
    plt.show()


if __name__ == '__main__':
    tick = input('Input ticker: ')
    period = input('Input interval(1m, 5m, etc): ')
    rng = int(input('Input candle range: '))
    main(tick, period, rng)
