import npimnearest
import npimcomparer
import npimcategorize


def images_to_html(np):
    print(f"Generate outputs/iindex.html")
    with open(f"outputs/iindex.html", "w") as f:
        f.write("<HTML><BODY><H1>NP Image Nearest Index</H1>\n")
        for iid in np.db[0].keys():
            im = np.get_im_by_iid(iid)
            f.write(f"<a href='ioutput_{iid}.html'>Image {iid} <img src='../images/{im.path}' height='50'/></a><br/>\n")
        f.write("</BODY></HTML>")
    for iid in np.db[0].keys():
        scores = np.search_by_im(iid)
        im = np.get_im_by_iid(iid)
        image_scores_to_html(im, scores)

def image_scores_to_html(im, scores):
    print(f"Generate outputs/ioutput_{im.id}.html")
    with open(f"outputs/ioutput_{im.id}.html","w") as f:
        f.write("<HTML><BODY><H1>NP Image Nearest</H1>\n")
        f.write(f"<p><a href='iindex.html'>Image Index</a>")
        f.write(f"<p><a href='pindex.html'>Product Index</a>")
        f.write(f"<p>Search Nearests images of {im.id} {im.name} <a href='../images/{im.path}'><img src='../images/{im.path}' height=100 /></a>\n")
        f.write(f"<p>Found {len(scores)} image(s)\n")
        for t in scores:
            im2 = np.get_im_by_iid(t[0])
            f.write(f"<p>Image: {im2.id} <a href='ioutput_{im2.id}.html'>{im2.name}</a> at {t[1]*100:.0f}%  <a href='../images/{im2.path}'><img src='../images/{im2.path}' height=100 /></a>\n")
            f.write(f"{npimcomparer.NPImageComparer().comp(im, im2)}")
        f.write("</BODY></HTML>")


def products_to_html(np):
    print(f"Generate outputs/pindex.html")
    with open(f"outputs/pindex.html", "w") as f:
        f.write("<HTML><BODY><H1>NP Product Nearest by image Index</H1>\n")
        for pid in np.db[1].keys():
            f.write(f"<a href='poutput_{pid}.html'>Product {pid}</a> ")
            for iid in np.db[1][pid]:
                im = np.get_im_by_iid(iid)
                f.write(f"<a href='poutput_{pid}.html'><img src='../images/{im.path}' height='50'/></a> ")
            f.write("<br/>\n")
        f.write("</BODY></HTML>")
    for pid in np.db[1].keys():
        scores = np.search_by_product(pid)
        product_scores_to_html(np, pid, scores)

def product_scores_to_html(np, pid, scores):
    print(f"Generate outputs/poutput_{pid}.html")
    with open(f"outputs/poutput_{pid}.html","w") as f:
        f.write("<HTML><BODY><H1>NP Product by image Nearest</H1>\n")
        f.write(f"<p><a href='pindex.html'>Index</a>")
        f.write(f"<p>Search Nearests products of product {pid}</p>")
        for iid in np.db[1][pid]:
            im = np.get_im_by_iid(iid)
            f.write(f"<a href='ioutput_{im.id}.html'><img src='../images/{im.path}' height='100'/></a> ")
        f.write("<br/>\n")
        f.write(f"<p>Found {len(scores)} product(s)\n")
        for t in scores:
            f.write(f"<p>Product {t[0]}  at {t[1]*100:.0f}% ")
            for iid in np.db[1][t[0]]:
                im = np.get_im_by_iid(iid)
                f.write(f"<a href='ioutput_{im.id}.html'><img src='../images/{im.path}' alt='{im.id}' height='100'/></a>")
            f.write(f"</p>\n")
        f.write("</BODY></HTML>")

def categorize_to_html(np):
    dico = {}
    npc = npimcategorize.NpImageCategorize()
    stop = 200
    for iid in np.db[0].keys():
        print(f"Predict iid: {iid}")
        stop -=1
        if stop == 0:
            break
        im = np.get_im_by_iid(iid)
        pred = npc.predict(im.path.replace("./","./images/"))
        label = npc.labels(pred)[0]
        s = label[1].replace(" ", "_")
        if s in dico:
            dico[s].append(im)
        else:
            dico[s] = [im]
    print(f"Generate outputs/c0index.html")
    with open(f"outputs/c0index.html", "w") as f:
        f.write("<HTML><BODY><H1>NP Product Category Index</H1>\n")
        for k in dico.keys():
            f.write(f"<a href='c{k}.html'>{k}</a><br/>\n")
        f.write("</BODY></HTML>")
    for k in dico.keys():
        print(f"Generate outputs/c{k}.html")
        with open(f"outputs/c{k}.html", "w") as f:
            f.write(f"<HTML><BODY><H1>{k}</H1>\n")
            for im in dico[k]:
                path = im.path.replace("./","../images/")
                f.write(f"<a href='{path}'><img src='{path}' height='100'/></a>\n")
            f.write("</BODY></HTML>")




if __name__ == '__main__':
    print("NPImageNearestHTML")
    print("==================")
    np = npimnearest.NPImageNearest("data/imagemock.h.pickle")
    # images_to_html(np)
    # products_to_html(np)
    categorize_to_html(np)