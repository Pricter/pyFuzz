import glob, subprocess, random, time, threading, os, hashlib

def fuzz(thr_id: int, inp: bytearray):
    assert isinstance(thr_id, int)
    assert isinstance(inp, bytearray)

    tmpfn = os.path.join("tmp", f"tmpinput{thr_id}")
    with open(tmpfn, "wb") as fd:
        fd.write(inp)

    sp = subprocess.Popen(["./objdump", "-x", tmpfn],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    ret = sp.wait()
    if ret != 0:
        print(f"ERROR: Exited with {ret}")

        if ret == -11:
            dahash = hashlib.sha256(inp).hexdigest()
            open(os.path.join("crashes", f"crash_{dahash:64}"),
                 "wb").write(inp)

corpus_filenames = glob.glob("corpus/*")

corpus = set()
for filename in corpus_filenames:
    corpus.add(open(filename, "rb").read())
corpus = list(map(bytearray, corpus))

start = time.time()
cases = 0
def worker(thr_id):
    global start, corpus, cases
    while True:
        inp = bytearray(random.choice(corpus))
        for _ in range(random.randint(1, 8)):
            inp[random.randint(0, len(inp) - 1)] = random.randint(0, 255)
        fuzz(thr_id, inp)
        cases += 1
        elapsed = time.time() - start
        fcps = float(cases) / elapsed
        if thr_id == 0:
            print(f"[{elapsed:10.4f}] cases {cases:10} | fcps {fcps:10.4f}")

for thr_id in range(24):
    threading.Thread(target=worker, args=[thr_id]).start()

while threading.active_count() > 0:
    time.sleep(0.1)
