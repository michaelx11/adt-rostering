import csv, random, sys

dances = ['han', 'yi', 'tibetan', 'classical', 'chaoxian', 'modernfusion', 'contemp', 'mymy', 'comebackhome', 'now', 'stopgirl', 'eternity', 'bts-medley']
#dances = ['han', 'yi', 'tibetan', 'classical', 'chaoxian', 'modernfusion', 'contemp', 'mymy', 'comebackhome', 'now-f', 'now-m', 'stopgirl', 'eternity', 'bts-medley']

teachers = ['Anita Liu', 'Angela Zhang', 'Helena Wang', 'Alice Lu', 'Alice Lu', 'Angela Zhang', 'Minerva Zhou', 'Kris Shin', 'Sally Lin', 'Minerva Zhou', 'Sally Lin', 'Weilian Chu', 'Sonya Han']

timeslots = ['M 7-8','M 8-9','M 9-10','M 10-11','T 7-8','T 8-9','T 9-10','T 10-11','W 7-8','W 8-9','W 9-10','W 10-11','R 7-8','R 8-9','R 9-10','R 10-11','F 7-8','F 8-9','F 9-10','F 10-11','S 2-3','S 3-4','S 4-5','Su 12-1','Su 1-2','Su 2-3','Su 3-4','Su 4-5','Su 5-6']

CANNOT_DROP = ['Minerva Zhou', 'Sally Lin', 'Angela Zhang', 'Kris Shin', 'Weilian Chu', 'Helena Wang', 'Sonya Han', 'Anita Liu', 'Alice Lu']

users = dict()

dance_assignments = dict()

class User:
    bad_slots = []
    prefs = []
    requested = None
    number = None

    def __init__(self, name):
        self.name = name

    def __str__(self):
        res = ''
        res += 'USER: ' + str(self.name) + '\n'
        res += 'Prefs: ' + str(self.prefs) + '\n'
        res += 'Bad Slots: ' + str(self.bad_slots) + '\n'
        res += 'Requested Num: ' + str(self.requested) + '\n'
        res += 'Number: ' + str(self.number) + '\n'
        return res

def readInScheduling():
    with open('scheduling.csv') as f:
        first = True
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if first:
                first = False
                continue
            name = row[0].strip()
            if name not in users:
                users[name] = User(name)
            users[name].bad_slots = map(lambda x: x == 'x', list(row[1:]))

def readInPrefs():
    count = 0
    with open('prefs.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if count < 3:
                count += 1
                continue
            name = row[0].strip()
            if name not in users:
                users[name] = User(name)
            users[name].number = row[1]
            users[name].requested = int(row[2]) if len(row[2]) > 0 else 1
            def tr(prefVal):
                if len(prefVal) > 0:
                    return float(prefVal)
                return 0.0

            users[name].prefs = map(tr, list(row[5:]))[:-1]
#            print name
#            print row

def readInAssignments():
    assignment = []
    with open('assignments.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            songname = row[0]
            dancers = list(row[1:])
            assignment.append(map(lambda x: users[x.strip()], dancers))
    return assignment

def readInGoogleAssignments():
    badPeople = []
    assignment = [[] for x in dances]
    count = 0
    with open('google-assignments.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if count < 3:
                count += 1
                continue
            name = row[0].strip()

            counter = 0
            for i in range(14):
                if row[5 + counter].lower().strip() == 'x':
                    assignment[counter].append(users[name.strip()])
                if i == 9:
                    continue
                counter += 1
    for i in range(len(teachers)):
        assignment[i].append(users[teachers[i]])


    return assignment


def checkDance(dance, threshold):
    if dance not in dances:
        print 'ERROR: %s not found!' % dance
        return
    danceIndex = dances.index(dance)
    print danceIndex
    possibleDancers = []
    for userKey in users:
        user = users[userKey]
        print userKey, user.prefs
        if user.prefs[danceIndex] >= threshold:
            possibleDancers.append(user)

    def compareByPref(a, b):
#        print danceIndex, a, b
        return cmp(b.prefs[danceIndex], a.prefs[danceIndex])
    possibleDancers = sorted(possibleDancers, compareByPref)
    print map(lambda x: x.name, possibleDancers)
    return possibleDancers

bestScore = 10000000
bestArrangement = {}
globalDropped = []
bestAssignments = set()
def checkFullAssignments(assignments):
    SINGLE_DANCE_USERS = list(CANNOT_DROP) 
    OPTIONS = []
    userCounts = {}
    for dance in assignments:
        OPTIONS.append(list(timeslots))

    for dance in assignments:
        for user in dance:
            if user.name in userCounts:
                userCounts[user.name] += 1
            else:
                userCounts[user.name] = 1
    for user in userCounts:
        if userCounts[user] == 1:
            SINGLE_DANCE_USERS.append(user)
    
    for imp in SINGLE_DANCE_USERS:
        count = 0
        for dance in assignments:
            for user in dance:
                if user.name == imp:
                    counter = 0
                    for isBadSlot in user.bad_slots:
                        if not isBadSlot:
                            counter += 1
                            continue
                        slot = timeslots[counter]
                        print dances[count] + ' ' + user.name + ' ' + slot + ' ' + str(counter)
                        if slot in OPTIONS[count]:
                            print 'Removed: ' + user.name + ' ' + dances[count] + ' ' + slot
                            OPTIONS[count].remove(slot)
                        counter += 1
            count += 1
    for thing in OPTIONS:
        print 'NUM OPTIONS: %d' % len(thing)

    used = {}
    for time in timeslots:
        used[time] = False


    mapping = {}
    def recur(i, currentScore):
        global bestScore, bestArrangement, globalDropped
        if currentScore > bestScore:
            return
        if i == 13:
            if currentScore == 0:
                bestAssignments.add(str(mapping))
            if currentScore < bestScore:
                print currentScore
                print mapping
                print globalDropped
            bestScore = currentScore
            bestArrangement = dict(mapping)
            return
        temp = list(OPTIONS[i])
        random.shuffle(temp)
        random.shuffle(temp)
        for time in temp:
            if not used[time]:
                mapping[dances[i]] = time
                used[time] = True
                prev = list(globalDropped)
                droppedDancers, additional = getDancersDropped(assignments[i], time)
                for dancer in droppedDancers:
                    globalDropped.append((dances[i], dancer))
                recur(i + 1, currentScore + additional) 
                globalDropped = prev
                mapping[dances[i]] = 'EMPTY'
                used[time] = False
    recur(0, 0)

    print "POSSIBLE ASSIGNMENTS: " + str(bestAssignments)

    return bestArrangement

def getAssignmentStats(assignments):
    userCounts = {}
    userPrefs = {}
    counter = 0
    for dance in assignments:
        for user in dance:
            prefLevel = user.prefs[counter]
            if user.name in userCounts:
                userCounts[user.name] += 1
            else:
                userCounts[user.name] = 1
            if user.name in userPrefs:
                userPrefs[user.name] = max(prefLevel, userPrefs[user.name])
            else:
                userPrefs[user.name] = prefLevel
        counter += 1
    print 'USER PREFS: '
    userPrefsList = []
    for userKey in userPrefs:
        userPrefsList.append((userKey, userPrefs[userKey]))

    def compare(a, b):
        return cmp(a[1], b[1])

    userPrefsList = sorted(userPrefsList, compare)
    missingUsers = []
    for user in users:
        if user not in userCounts:
            missingUsers.append(user)
    return missingUsers, userPrefsList


def checkTiming(userList):
    timeDict = {}
    count = 0
    for time in timeslots:
        print 'TIME: ' + time + '\n\n'
        timeDict[time] = []
        for user in userList:
            if user.bad_slots[count] == False:
                timeDict[time].append(user)
                print user.name
        print '\nCan make: %d' % len(timeDict[time])
        print '\n'
        count += 1
    return timeDict

def getDancersDropped(userList, time):
    bad_count = 0
    dropped = []
    timeIndex = timeslots.index(time)
    for user in userList:
        if user.bad_slots[timeIndex]:
            dropped.append(user.name)
            bad_count += 1
    return dropped, bad_count

readInScheduling()
readInPrefs()
for user in users:
    print users[user]
    print len(users[user].prefs)
#print len(dances)

print len(timeslots)
#assignment = readInAssignments()
assignment = readInGoogleAssignments()
print assignment
print getAssignmentStats(assignment)
print checkFullAssignments(assignment)
