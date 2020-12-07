import time
import npproductnearest
import config


def to_html(np):
    print(f"Generate outputs/index.html")
    with open(f"outputs/index.html", "w") as f:
        f.write('<HTML><HEAD></HEAD><BODY><H1>NPNearest Products Index</H1>\n')
        for k in np.db.keys():
            try:
                p = np.get_by_id(k)
                f.write(f"<a href='output_{k}.html'>Product {k}</a>: {np.db[k].l[0].val}<br/>")
            except:
                pass
        f.write("</BODY></HTML>")
    for k in np.db.keys():
        p = np.get_by_id(k)
        scores = np.search(k, 10)
        scores_to_html(np, p, scores)

def scores_to_html(np, p, scores):
    print(f"Generate outputs/output_{p.id}.html")
    with open(f"outputs/output_{p.id}.html","w") as f:
        f.write('<HTML><HEAD></HEAD><BODY><H1>NPNearest</H1>\n')
        f.write(f"<p><a href='index.html'>Index</a>")
        f.write(f"<p>Search Nearests products of {p.id}\n")
        f.write(f"<p>Found {len(scores)} product(s)\n")
        for t in scores:
            p2 = np.get_by_id(t[0])
            f.write(f"<p>Product: <a href='output_{p2.id}.html'>{p2.id}</a> at {t[1]*100:.0f}% \n")
            f.write((f"(USE: {np.diff.compare_product(p, p2) * 100:.0f}%, Gestalt: {np.diff.compare_product_gestalt(p, p2) * 100:.0f}%)"))
            f.write(f"<table border='1'><tr><td>cid</td><td>{p.id} values</td><td>{p2.id} values</td><td>Score USE</td><td>Weights USE</td><td>Scores Gestalt</td><td>Weights Gestalt</td></tr>\n")
            res2 = np.diff.compare_product_to_scores(p, p2)
            total2 = sum([w[1] for w in res2])
            res3 = np.diff.compare_product_gestalt_to_scores(p, p2)
            total3 = sum([w[1] for w in res3])
            i = 0
            for t in res2:
                c = p.l[i]
                c2 = p2.get_car_by_id(c.id)
                f.write(f"<tr><td>{c.id}</td><td>{'' if c is None else c.val}</td><td>{'' if c2 is None else c2.val}</td>")
                f.write(f"<td>{t[0]*100:.0f}%</td><td>{t[1] / total2:.2f}</td><td>{res3[i][0]*100:.0f}%</td><td>{res3[i][1] / total3:.2f}</td></tr>\n")
                i+=1
            f.write(f"</table>")
        f.write("</BODY></HTML>")


if __name__ == '__main__':
    print("NPNearestHTML")
    print("=============")
    print(f"V{config.version}")
    np = npproductnearest.NPNearest("data/data.h.pickle")
    to_html(np)

