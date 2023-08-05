import os


def is_yes(m):
    return input(m).lower().startswith("y")


def add_commas(num, num_digits=3, delim=","):
    num_str = str(num)

    str_list = []
    while len(num_str):
        str_list.append(num_str[-num_digits:])
        num_str = num_str[:-num_digits]

    str_list.reverse()

    return delim.join(str_list)


def run():

    while True:
        d = input("directory? ")
        if len(d) == 0:
            break

        d = os.path.abspath(d)

        sort_by_ext = {}

        dir_names = []
        dir_sizes = []
        file_number_list = []
        cnt = 1
        number_of_errors = 0
        for root, dirs, files in os.walk(d, followlinks=True):
            dir_names.append(root)
            try:
                dir_sizes.append(sum([os.path.getsize(os.path.join(root, name)) for name in files]))
            except (FileNotFoundError, OSError):
                dir_sizes.append(0)
                number_of_errors += 1

            file_number_list.append(len(files))

            for file in files:
                r, e = os.path.splitext(file)

                if e in sort_by_ext:
                    sort_by_ext[e] += 1
                else:
                    sort_by_ext[e] = 1

            print("\r%d" % cnt, end="")
            cnt += 1

        print(" directories...")
        print("Error(s) occured in %d directories..." % number_of_errors)

        n = len(dir_names)

        if n == 0:
            continue

        assert len(dir_sizes) == n
        assert len(file_number_list) == n

        assert dir_names[0] == d
        dir_size_dict = {"": dir_sizes[0]}
        total_size = dir_sizes[0]

        dir_name_length = len(d)

        if d[-1] == os.path.sep:
            dir_name_length -= 1

        for i in range(1, n):
            dir_name = dir_names[i]
            dir_size = dir_sizes[i]

            assert len(dir_name) > dir_name_length
            rel_name = dir_name[dir_name_length + 1:]

            depth1_subdir, sep, tail = rel_name.partition(os.path.sep)

            if (depth1_subdir) in dir_size_dict:
                dir_size_dict[depth1_subdir] += dir_size
            else:
                dir_size_dict[depth1_subdir] = dir_size

            total_size += dir_size

        max_length = len(add_commas(total_size))
        print(add_commas(total_size))

        dirlist = [(dirname, dir_size_dict[dirname]) for dirname in dir_size_dict]

        def cmp(x, y, kind):
            if kind == "name":
                x = x[0].lower()
                y = y[0].lower()
            elif kind == "size":
                x = x[1]
                y = y[1]
            else:
                assert False

            if x < y:
                return -1
            elif x > y:
                return 1
            else:
                return 0

        if is_yes("sort by name? "):
            dirlist.sort(key=lambda x: x[0])
        else:
            dirlist.sort(key=lambda x: x[1])

        for dir_name, size in dirlist:
            print("%s %s%s%s" % (add_commas(size).rjust(max_length), os.curdir, os.path.sep, dir_name))

        keys = list(sort_by_ext.keys())
        keys.sort()

        print("")
        if is_yes("Do you want to print # files for each extension? "):
            for key in keys:
                print("%s: %d" % (key, sort_by_ext[key]))

        print("")


if __name__ == "__main__":
    run()
