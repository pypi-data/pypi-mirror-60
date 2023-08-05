# this module allows for conversion from standerd time to 00:00:00 format

def convert_six (time):
    if '12' in time and 'am' in time:
        minn = time[3:5]
        return '00:' + minn + ':00'
    elif '12' in time and 'pm' in time:
        minn = time[3:5]
        return '12:' + minn + ':00'
    elif 'am' in time:
        t_striped = time.replace('am', '')
        t_split = t_striped.split(':')
        if len(t_split[0]) == 1:
            t_split[0] = '0' + t_split[0]
        new_time = t_split[0]+ ':' + t_split[1] + ':' + '00'
        return new_time
    else:
        t_striped = time.replace('pm', '')
        t_split = t_striped.split(':')
        t_split[0] = str( int(t_split[0]) + 12 )
        new_time = t_split[0]+ ':' + t_split[1] + ':' + '00'
        return new_time

def convert_stan(time):
    t_split = time.split(':')
    if int(t_split[0]) >  12 :
        one_st= str(int(t_split[0]) - 12)
        new_time = one_st +':'+ t_split[1] + 'pm'
        return new_time
    
    elif int(t_split[0]) ==  12 :
        new_time = t_split[0] +':'+ t_split[1] + 'pm'
        return new_time
    elif '00:00:00' in time:
        return '12:00am'
    else:
        new_time = t_split[0] +':'+ t_split[1] + 'am'
        return new_time

def convert_mil(time):
    if 'am' in time or 'pm' in time:
        six_dig = convert_six(time)
        t_striped = six_dig.replace(':', '')
        new_time = t_striped[0:4]
        return new_time
    else:
        t_striped = time.replace(':', '')
        new_time = t_striped[0:4]
        return new_time 

def convert(time):
    military = ''
    six_figure = ''
    standard = ''
    if 'am' in time or 'pm' in time:
        standard = time
        military = convert_mil(time)
        six_figure = convert_six(time)
    elif len(time) > 4:
        standard = convert_stan(time)
        military = convert_mil(time)
        six_figure = time
    else:
        first = time [0:2]
        second = time[2:]
        military = time
        six_figure = first +':'+ second +':00'
        standard = convert_stan(six_figure)

    return {
        'military' : military,
        'six_figure' : six_figure,
        'standard' : standard
    }

if __name__ == "__main__":
    print('Insert number for automatic conversion')
    time = input('Input Time : ')
    response = convert(time)
    print(response)