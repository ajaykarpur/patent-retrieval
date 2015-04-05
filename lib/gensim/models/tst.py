import numpy, random, itertools

hellinger = lambda v1, v2: numpy.sqrt(0.5 * ((numpy.sqrt(v1) - numpy.sqrt(v2))**2).sum())

def get_dist(m):
    """Return normalized topic matrix for LDA model `m`."""
    l = m.state.get_lambda()
    for i in range(m.num_topics):
        l[i] /= l[i].sum()
    return l

def find_closest_vec(v1, l2):
    """Find index of the closest vector to v1 in the topic vectors l2"""
    return min((hellinger(v1, l2[i]), i) for i in xrange(len(l2)))[1]

def find_closest(l1, l2):
    """For each topic vector in l1, find index of the hellinger-closest vector in l2"""
    return [find_closest_vec(v1, l2) for v1 in l1]

def max_dist(l1, l2):
    """Find the furthest indexes between closest matches, for two topic matrices."""
    return max(numpy.abs(numpy.arange(len(l1)) - find_closest(l1, l2)))

def best_ordering(l1, l2):
    """
    Return the best topic orderings so that m1 topics are in decreasing alpha
    and m2 topics have the smallest distance possible to the nearest m1 topic.

    """
    assert len(l1) == len(l2)
    best, bestdist = None, len(l1)
    for i in xrange(5000):
        ordering = range(len(l2))
        random.shuffle(ordering)
        dist = max_dist(l1, l2[ordering])
        if dist < bestdist:
            best = ordering
            bestdist = dist
    return bestdist, best

def greedy_ordering(l1, l2):
    result = []
    for i, v1 in enumerate(l1):
        closest = sorted([(hellinger(v1, l2[i]), i) for i in xrange(len(l2))])
        for j, (dist, index) in enumerate(closest):
            if index not in result:
                result.append(index)
                break
    return -1, result


def get_topics(m, ordering):
    return ['%s' % ', '.join(word for _, word in m.show_topic(ordering[i], topn=5)) for i in range(m.num_topics)]


def format(m1, m2):
    auto_order = numpy.argsort(m1.alpha)[::-1]
    l1, l2 = get_dist(m1)[auto_order], get_dist(m2)
    # best_dist, matched = best_ordering(l1, l2)
    best_dist, matched = greedy_ordering(l1, l2)
    print best_dist, matched
    l2 = l2[matched]
    # print bestdist, max_dist(l1, l2[matched])

    topics = zip(get_topics(m1, auto_order), get_topics(m2, matched))
    for i, (t1, t2) in enumerate(topics):
        interesting1 = '' if i == find_closest_vec(l1[i], l2) else 'class="different"'
        interesting2 = '' if i == find_closest_vec(l2[i], l1) else 'class="different"'
        print '<tr><td>#%s</td><td id="m%i" %s data-id="n%i">%.3f: %s</td><td id="n%i" %s data-id="m%i">%s</td></tr>' % \
            (i,
            i, interesting1, find_closest_vec(l1[i], l2), m1.alpha[auto_order][i], t1,
            i, interesting2, find_closest_vec(l2[i], l1), t2)

def format2(m1, m2):
    auto_order = numpy.argsort(m1.alpha)[::-1]
    l1, l2 = get_dist(m1)[auto_order], get_dist(m2)
    # best_dist, matched = best_ordering(l1, l2)
    best_dist, matched = greedy_ordering(l1, l2)
    print best_dist, matched
    l2 = l2[matched]
    # print bestdist, max_dist(l1, l2[matched])

    topics = zip(get_topics(m1, auto_order), get_topics(m2, matched))
    rows = []
    for i, (t1, t2) in enumerate(topics):
        match1, match2 = find_closest_vec(l1[i], l2), find_closest_vec(l2[i], l1)
        interesting1 = '' if find_closest_vec(l2[match1], l1) == i else 'class="different"'
        interesting2 = '' if find_closest_vec(l1[match2], l2) == i else 'class="different"'
        # interesting2 = '' if i == match2 else 'class="different"'
        rows.append('<td id="m%i" %s data-id="n%i">%s</td><td id="n%i" %s data-id="m%i">%s</td>' % \
            (i, interesting1, match1, t1,
            i, interesting2, match2, t2))
    for i in xrange(len(rows) / 2):
        other = i + len(rows) / 2
        # print '<tr><td>#%s</td>%s<td>#%s</td>%s</tr>' % (i, rows[i], other, rows[other])
        print '<tr>%s%s</tr>' % (rows[i], rows[other])
