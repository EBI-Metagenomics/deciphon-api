FILE *fdopen(int, const char *);
int fclose(FILE *);

typedef void sched_logger_print_t(char const *msg, void *arg);
void sched_logger_setup(sched_logger_print_t *print, void *arg);

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
};

struct sched_db;
struct sched_job;
struct sched_prod;
struct sched_seq;

extern "Python" void prod_set_cb(struct sched_prod *prod, void *arg);
extern "Python" void seq_set_cb(struct sched_seq *seq, void *arg);
extern "Python" void logger_cb(char const *msg, void *arg);
extern "Python" void db_set_cb(struct sched_db *db, void *arg);

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
    ERROR_SIZE = 256,
};

struct sched_db
{
    int64_t id;
    int64_t xxh64;
    char filename[FILENAME_SIZE];
};

typedef void(sched_db_set_cb)(struct sched_db *db, void *arg);

enum sched_rc sched_db_get(struct sched_db *db);
enum sched_rc sched_db_add(struct sched_db *db, char const *filename);
enum sched_rc sched_db_get_all(sched_db_set_cb cb, struct sched_db *db,
                               void *arg);

enum sched_job_state
{
    SCHED_JOB_PEND,
    SCHED_JOB_RUN,
    SCHED_JOB_DONE,
    SCHED_JOB_FAIL
};

struct sched_job
{
    int64_t id;

    int64_t db_id;
    int32_t multi_hits;
    int32_t hmmer3_compat;
    char state[JOB_STATE_SIZE];

    char error[JOB_ERROR_SIZE];
    int64_t submission;
    int64_t exec_started;
    int64_t exec_ended;
};

typedef void(sched_seq_set_cb)(struct sched_seq *seq, void *arg);
typedef void(sched_prod_set_cb)(struct sched_prod *prod, void *arg);

void sched_job_init(struct sched_job *job, int64_t db_id, bool multi_hits,
                    bool hmmer3_compat);

enum sched_rc sched_job_get_seqs(int64_t job_id, sched_seq_set_cb cb,
                                 struct sched_seq *seq, void *arg);

enum sched_rc sched_job_get_prods(int64_t job_id, sched_prod_set_cb cb,
                                  struct sched_prod *prod, void *arg);

enum sched_rc sched_job_get(struct sched_job *job);

enum sched_rc sched_job_set_run(int64_t job_id);
enum sched_rc sched_job_set_fail(int64_t job_id, char const *msg);
enum sched_rc sched_job_set_done(int64_t job_id);

enum sched_rc sched_job_begin_submission(struct sched_job *job);
void sched_job_add_seq(struct sched_job *job, char const *name,
                       char const *data);
enum sched_rc sched_job_rollback_submission(void);
enum sched_rc sched_job_end_submission(struct sched_job *job);

enum sched_rc sched_job_next_pend(struct sched_job *job);

struct sched_prod
{
    int64_t id;

    int64_t job_id;
    int64_t seq_id;

    char profile_name[PROFILE_NAME_SIZE];
    char abc_name[ABC_NAME_SIZE];

    double alt_loglik;
    double null_loglik;

    char profile_typeid[PROFILE_TYPEID_SIZE];
    char version[VERSION_SIZE];

    char match[MATCH_SIZE];
};

typedef int(sched_prod_write_match_cb)(FILE *fp, void const *match);

enum sched_rc sched_prod_get(struct sched_prod *prod);
enum sched_rc sched_prod_add(struct sched_prod *prod);
enum sched_rc sched_prod_add_file(FILE *fp);

enum sched_rc sched_setup(char const *filepath);
enum sched_rc sched_open(void);
enum sched_rc sched_close(void);

struct sched_seq
{
    int64_t id;
    int64_t job_id;
    char name[SEQ_NAME_SIZE];
    char data[SEQ_SIZE];
};

enum sched_rc sched_seq_next(struct sched_seq *seq);
enum sched_rc sched_seq_get(struct sched_seq *seq);
