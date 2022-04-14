FILE *fdopen(int, const char *);
int fclose(FILE *);

enum sched_rc
{
    SCHED_OK,
    SCHED_END,
    SCHED_NOTFOUND,
    SCHED_EFAIL,
    SCHED_EIO,
    SCHED_EINVAL,
    SCHED_ENOMEM,
    SCHED_EPARSE,
    SCHED_ECONSTRAINT,
};

struct sched_db;
struct sched_job;
struct sched_prod;
struct sched_scan;
struct sched_seq;

extern "Python" void append_db(struct sched_db *, void *arg);
extern "Python" void append_hmm(struct sched_hmm *, void *arg);
extern "Python" void append_scan(struct sched_scan *, void *arg);
extern "Python" void append_job(struct sched_job *, void *arg);
extern "Python" void append_prod(struct sched_prod *, void *arg);
extern "Python" void append_seq(struct sched_seq *, void *arg);
extern "Python" void sched_logger_print(char const *ctx, char const *msg,
                                        void *arg);

enum sched_limits
{
    ABC_NAME_SIZE = 16,
    FILENAME_SIZE = 128,
    JOB_ERROR_SIZE = 256,
    JOB_STATE_SIZE = 5,
    MATCH_SIZE = 5 * (1024 * 1024),
    MAX_NUM_THREADS = 64,
    NUM_SEQS_PER_JOB = 64,
    PATH_SIZE = 4096,
    PROFILE_NAME_SIZE = 64,
    PROFILE_TYPEID_SIZE = 16,
    SEQ_NAME_SIZE = 256,
    SEQ_SIZE = (1024 * 1024),
    VERSION_SIZE = 16,
};

typedef void(sched_db_set_func_t)(struct sched_db *, void *arg);
typedef void(sched_hmm_set_func_t)(struct sched_hmm *, void *arg);
typedef void(sched_job_set_func_t)(struct sched_job *, void *arg);
typedef void(sched_prod_set_func_t)(struct sched_prod *, void *arg);
typedef void(sched_scan_set_func_t)(struct sched_scan *, void *arg);
typedef void(sched_seq_set_func_t)(struct sched_seq *, void *arg);

/* --- SCHED Section --- */
struct sched_health
{
    FILE *fp;
    int num_errors;
};

enum sched_rc sched_init(char const *filepath);
enum sched_rc sched_cleanup(void);
enum sched_rc sched_health_check(struct sched_health *);
enum sched_rc sched_wipe(void);

/* --- LOGGER Section --- */
typedef void (*sched_logger_print_func_t)(char const *ctx, char const *msg,
                                          void *arg);
void sched_logger_setup(sched_logger_print_func_t, void *arg);

/* --- DB Section --- */
struct sched_db
{
    int64_t id;
    int64_t xxh3;
    char filename[FILENAME_SIZE];
    int64_t hmm_id;
};

void sched_db_init(struct sched_db *);

enum sched_rc sched_db_get_by_id(struct sched_db *, int64_t id);
enum sched_rc sched_db_get_by_xxh3(struct sched_db *, int64_t xxh3);
enum sched_rc sched_db_get_by_filename(struct sched_db *, char const *filename);

enum sched_rc sched_db_get_all(sched_db_set_func_t, struct sched_db *,
                               void *arg);

enum sched_rc sched_db_add(struct sched_db *, char const *filename);

enum sched_rc sched_db_remove(int64_t id);

/* --- HMM Section --- */
struct sched_hmm
{
    int64_t id;
    int64_t xxh3;
    char filename[FILENAME_SIZE];
    int64_t job_id;
};

void sched_hmm_init(struct sched_hmm *);
enum sched_rc sched_hmm_set_file(struct sched_hmm *, char const *filename);

enum sched_rc sched_hmm_get_by_id(struct sched_hmm *, int64_t id);
enum sched_rc sched_hmm_get_by_job_id(struct sched_hmm *, int64_t job_id);
enum sched_rc sched_hmm_get_by_xxh3(struct sched_hmm *, int64_t xxh3);
enum sched_rc sched_hmm_get_by_filename(struct sched_hmm *,
                                        char const *filename);

enum sched_rc sched_hmm_get_all(sched_hmm_set_func_t, struct sched_hmm *,
                                void *arg);

enum sched_rc sched_hmm_remove(int64_t id);

/* --- JOB Section --- */
enum sched_job_type
{
    SCHED_SCAN,
    SCHED_HMM
};

enum sched_job_state
{
    SCHED_PEND,
    SCHED_RUN,
    SCHED_DONE,
    SCHED_FAIL
};

struct sched_job
{
    int64_t id;
    int type;

    char state[JOB_STATE_SIZE];
    int progress;
    char error[JOB_ERROR_SIZE];

    int64_t submission;
    int64_t exec_started;
    int64_t exec_ended;
};

void sched_job_init(struct sched_job *, enum sched_job_type);

enum sched_rc sched_job_get_by_id(struct sched_job *, int64_t id);
enum sched_rc sched_job_next_pend(struct sched_job *);
enum sched_rc sched_job_get_all(sched_job_set_func_t, struct sched_job *,
                                void *arg);

enum sched_rc sched_job_set_run(int64_t id);
enum sched_rc sched_job_set_fail(int64_t id, char const *msg);
enum sched_rc sched_job_set_done(int64_t id);

enum sched_rc sched_job_submit(struct sched_job *, void *actual_job);

enum sched_rc sched_job_add_progress(int64_t id, int progress);

enum sched_rc sched_job_remove(int64_t id);

/* --- SCAN Section --- */
struct sched_scan
{
    int64_t id;
    int64_t db_id;

    int multi_hits;
    int hmmer3_compat;

    int64_t job_id;
};

void sched_scan_init(struct sched_scan *, int64_t db_id, bool multi_hits,
                     bool hmmer3_compat);

enum sched_rc sched_scan_get_seqs(int64_t job_id, sched_seq_set_func_t,
                                  struct sched_seq *seq, void *arg);

enum sched_rc sched_scan_get_prods(int64_t job_id, sched_prod_set_func_t,
                                   struct sched_prod *prod, void *arg);

enum sched_rc sched_scan_get_by_id(struct sched_scan *, int64_t scan_id);
enum sched_rc sched_scan_get_by_job_id(struct sched_scan *, int64_t job_id);

void sched_scan_add_seq(struct sched_scan *, char const *name,
                        char const *data);

enum sched_rc sched_scan_get_all(sched_scan_set_func_t fn, struct sched_scan *,
                                 void *arg);

/* --- PROD Section --- */
struct sched_prod
{
    int64_t id;

    int64_t scan_id;
    int64_t seq_id;

    char profile_name[PROFILE_NAME_SIZE];
    char abc_name[ABC_NAME_SIZE];

    double alt_loglik;
    double null_loglik;

    char profile_typeid[PROFILE_TYPEID_SIZE];
    char version[VERSION_SIZE];

    char match[MATCH_SIZE];
};

typedef int(sched_prod_write_match_func_t)(FILE *fp, void const *match);

void sched_prod_init(struct sched_prod *, int64_t scan_id);
enum sched_rc sched_prod_get_by_id(struct sched_prod *, int64_t id);
enum sched_rc sched_prod_add(struct sched_prod *);
enum sched_rc sched_prod_add_file(FILE *fp);

enum sched_rc sched_prod_write_begin(struct sched_prod const *,
                                     unsigned file_num);
enum sched_rc sched_prod_write_match(sched_prod_write_match_func_t *,
                                     void const *match, unsigned file_num);
enum sched_rc sched_prod_write_match_sep(unsigned file_num);
enum sched_rc sched_prod_write_end(unsigned file_num);

enum sched_rc sched_prod_get_all(sched_prod_set_func_t fn, struct sched_prod *,
                                 void *arg);

/* --- SEQ Section --- */
struct sched_seq
{
    int64_t id;
    int64_t scan_id;
    char name[SEQ_NAME_SIZE];
    char data[SEQ_SIZE];
};

void sched_seq_init(struct sched_seq *seq, int64_t scan_id, char const *name,
                    char const *data);

enum sched_rc sched_seq_get_by_id(struct sched_seq *, int64_t id);
enum sched_rc sched_seq_scan_next(struct sched_seq *);
enum sched_rc sched_seq_get_all(sched_seq_set_func_t fn, struct sched_seq *,
                                void *arg);
