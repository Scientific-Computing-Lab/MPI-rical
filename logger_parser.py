import matplotlib.pyplot as plt
import datetime
import re

PATH = 'git_repos_logger.txt'


def logger_read():
    txt = ''
    with open(PATH) as f:
        for line in f.readlines():
            txt += line
    return txt


def repos_num():
    return [int(num) for num in re.findall(' [0-9]+ ', repo_logger)]


def repos_dates():
    dates = re.findall('[0-9]+-[0-9]+-[0-9]+', repo_logger)
    del dates[::2]
    return [datetime.datetime.strptime(date, '%Y-%m-%d') for date in dates]


def plot_repos_per_month(dates, numbers):
    plt.plot(dates, numbers, marker='o')
    plt.fill_between(dates, min(numbers), numbers, alpha=0.7)
    plt.title('Number of MPI Repos')
    plt.ylabel('Number of Repos')
    plt.xlabel('Year')
    plt.show()


repo_logger = logger_read()
numbers = repos_num()
dates = repos_dates()
print(f'Number of MPI Repos: {sum(numbers)}')
plot_repos_per_month(dates, numbers)
