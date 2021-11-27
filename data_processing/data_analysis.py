##

def scatter_by_hours(df):
    grouped = df.groupby(by=['OpenTime', 'CloseTime'])
    for idx, group_tuple in enumerate(grouped):
        df.loc[group_tuple[1].index, 'timegroup'] = idx+1
        print(f"{idx}: {group_tuple[0]}")
    df.plot.scatter('lat_n', 'lng_n', c='timegroup', colormap='viridis')
    plt.show()
