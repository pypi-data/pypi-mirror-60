from __future__ import print_function


def isyes(m):
    return input( m ).lower().startswith( 'y' )

def addcommas(num,ndigit=3,delim=','):
    s = str(num)

    l = []
    while len(s):
        l.append(s[-ndigit:])
        s = s[:-ndigit]

    l.reverse()

    return delim.join(l)

if __name__ == "__main__":
    import os, sys

    while True:
        #sys.stdout.write('directory? ')
        #d = sys.stdin.readline()
        d = input( 'directory? ')
        if len(d) == 0:
            break

        d = os.path.abspath(d)

        sort_by_ext = {}

        dirnames = []
        dirsizes = []
        filenums = []
        cnt = 1
        numerrs = 0
        for root, dirs, files in os.walk(d,followlinks=True):
            dirnames.append(root)
            try:
                dirsizes.append(sum([os.path.getsize(os.path.join(root, name)) for name in files]))
            except (FileNotFoundError, OSError) as e:
                #print( e, e.__class__ )
                dirsizes.append(0)
                numerrs += 1

            filenums.append(len(files))

            for file in files:
                r, e = os.path.splitext(file)

                if e in sort_by_ext:
                    sort_by_ext[e] += 1
                else:
                    sort_by_ext[e] = 1


            print ( '\r%d' % cnt, end = '' )
            cnt += 1

            #if 'CVS' in dirs:
            #    dirs.remove('CVS')  # don't visit CVS directories
        print( ' directories...' )
        print( 'Error(s) occured in %d directories...' % numerrs )

        n = len(dirnames)

        if n == 0:
            continue


        assert len(dirsizes) == n
        assert len(filenums) == n

        assert dirnames[0] == d
        mydu = {'': dirsizes[0]}
        tsize = dirsizes[0]

        dlen = len(d)

        if d[-1] == os.path.sep:
            dlen -= 1

        for i in range(1,n):
            dirname = dirnames[i]
            dirsize = dirsizes[i]

            assert len(dirname) > dlen
            relname = dirname[dlen+1:]

            depth1subdir, sep, tail = relname.partition(os.path.sep)

            if (depth1subdir) in mydu:
                mydu[depth1subdir] += dirsize
            else:
                mydu[depth1subdir] = dirsize

            tsize += dirsize

        maxlen = len(addcommas(tsize))
        print( addcommas(tsize) )

        dirlist = [ (dirname, mydu[dirname] ) for dirname in mydu]

        def cmp(x,y,kind):
            if kind == 'name':
                x = x[0].lower()
                y = y[0].lower()
            elif kind == 'size':
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

        if isyes( 'sort by name? ' ):
            #dirlist.sort(lambda x, y: cmp(x,y,'name'))
            dirlist.sort( key = lambda x: x[0] )
        else:
            #dirlist.sort(lambda x, y: cmp(x,y,'size'))
            dirlist.sort( key = lambda x: x[1] )

        for dirname, size in dirlist:
            print( '%s %s%s%s' % ( addcommas(size).rjust(maxlen), os.curdir, os.path.sep, dirname ) )

        keys = list(sort_by_ext.keys())
        keys.sort()

        print( '' )
        if isyes( 'Do you want to print # files for each extension? ' ):
            for key in keys:
                print( '%s: %d' % (key,sort_by_ext[key]) )

        print( '' )



