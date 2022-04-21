FILE *fdopen(int, const char *);
int fclose(FILE *);

extern "Python" void append_db(struct sched_db *, void *arg);
extern "Python" void append_hmm(struct sched_hmm *, void *arg);
extern "Python" void append_scan(struct sched_scan *, void *arg);
extern "Python" void append_job(struct sched_job *, void *arg);
extern "Python" void append_prod(struct sched_prod *, void *arg);
extern "Python" void append_seq(struct sched_seq *, void *arg);
