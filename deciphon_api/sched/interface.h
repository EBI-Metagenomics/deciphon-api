FILE *fdopen(int, const char *);
int fclose(FILE *);

extern "Python" void append_db(struct sched_db *, void *arg);
extern "Python" void append_hmm(struct sched_hmm *, void *arg);
extern "Python" void append_scan(struct sched_scan *, void *arg);
extern "Python" void append_job(struct sched_job *, void *arg);
extern "Python" void append_prod(struct sched_prod *, void *arg);
extern "Python" void append_seq(struct sched_seq *, void *arg);

/* --- limits.h file --- */

enum sched_limits
{
    SCHED_ABC_NAME_SIZE = 16,
    SCHED_FILENAME_SIZE = 128,
    SCHED_JOB_ERROR_SIZE = 256,
    SCHED_JOB_STATE_SIZE = 5,
    SCHED_MATCH_SIZE = 5 * (1024 * 1024),
    SCHED_MAX_NUM_THREADS = 64,
    SCHED_NUM_SEQS_PER_JOB = 512,
    SCHED_PATH_SIZE = 4096,
    SCHED_PROFILE_NAME_SIZE = 64,
    SCHED_PROFILE_TYPEID_SIZE = 16,
    SCHED_SEQ_NAME_SIZE = 256,
    SCHED_SEQ_SIZE = (1024 * 1024),
    SCHED_VERSION_SIZE = 16,
};

/* --- rc.h file --- */

enum sched_rc
{
    SCHED_OK,
    SCHED_END,
    SCHED_HMM_NOT_FOUND,
    SCHED_SCAN_NOT_FOUND,
    SCHED_DB_NOT_FOUND,
    SCHED_JOB_NOT_FOUND,
    SCHED_PROD_NOT_FOUND,
    SCHED_SEQ_NOT_FOUND,
    SCHED_NOT_ENOUGH_MEMORY,
    SCHED_FAIL_PARSE_FILE,
    SCHED_FAIL_OPEN_FILE,
    SCHED_FAIL_CLOSE_FILE,
    SCHED_FAIL_WRITE_FILE,
    SCHED_FAIL_READ_FILE,
    SCHED_FAIL_REMOVE_FILE,
    SCHED_INVALID_FILE_NAME,
    SCHED_INVALID_FILE_NAME_EXT,
    SCHED_TOO_SHORT_FILE_NAME,
    SCHED_TOO_LONG_FILE_NAME,
    SCHED_TOO_LONG_FILE_PATH,
    SCHED_FILE_NAME_NOT_SET,
    SCHED_HMM_ALREADY_EXISTS,
    SCHED_DB_ALREADY_EXISTS,
    SCHED_ASSOC_HMM_NOT_FOUND,
    SCHED_FAIL_BIND_STMT,
    SCHED_FAIL_EVAL_STMT,
    SCHED_FAIL_GET_FRESH_STMT,
    SCHED_FAIL_GET_COLUMN_TEXT,
    SCHED_FAIL_EXEC_STMT,
    SCHED_FAIL_PREPARE_STMT,
    SCHED_FAIL_RESET_STMT,
    SCHED_FAIL_OPEN_SCHED_FILE,
    SCHED_FAIL_CLOSE_SCHED_FILE,
    SCHED_SQLITE3_NOT_THREAD_SAFE,
    SCHED_SQLITE3_TOO_OLD,
    SCHED_FAIL_BEGIN_TRANSACTION,
    SCHED_FAIL_END_TRANSACTION,
    SCHED_FAIL_ROLLBACK_TRANSACTION,
};

/* --- structs.h file --- */

struct sched_scan
{
    int64_t id;
    int64_t db_id;

    int multi_hits;
    int hmmer3_compat;

    int64_t job_id;
};

struct sched_hmm
{
    int64_t id;
    int64_t xxh3;
    char filename[SCHED_FILENAME_SIZE];
    int64_t job_id;
};

struct sched_db
{
    int64_t id;
    int64_t xxh3;
    char filename[SCHED_FILENAME_SIZE];
    int64_t hmm_id;
};

struct sched_prod
{
    int64_t id;

    int64_t scan_id;
    int64_t seq_id;

    char profile_name[SCHED_PROFILE_NAME_SIZE];
    char abc_name[SCHED_ABC_NAME_SIZE];

    double alt_loglik;
    double null_loglik;

    char profile_typeid[SCHED_PROFILE_TYPEID_SIZE];
    char version[SCHED_VERSION_SIZE];

    char match[SCHED_MATCH_SIZE];
};

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

    char state[SCHED_JOB_STATE_SIZE];
    int progress;
    char error[SCHED_JOB_ERROR_SIZE];

    int64_t submission;
    int64_t exec_started;
    int64_t exec_ended;
};

struct sched_seq
{
    int64_t id;
    int64_t scan_id;
    char name[SCHED_SEQ_NAME_SIZE];
    char data[SCHED_SEQ_SIZE];
};

/* --- sched.h file --- */

struct sched_health
{
    FILE *fp;
    int num_errors;
};

enum sched_rc sched_init(char const *filepath);
enum sched_rc sched_cleanup(void);
enum sched_rc sched_health_check(struct sched_health *);
enum sched_rc sched_wipe(void);

/* --- hmm.h file --- */

typedef void(sched_hmm_set_func_t)(struct sched_hmm *, void *arg);

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

/* --- db.h file --- */

typedef void(sched_db_set_func_t)(struct sched_db *, void *arg);

void sched_db_init(struct sched_db *);

enum sched_rc sched_db_get_by_id(struct sched_db *, int64_t id);
enum sched_rc sched_db_get_by_xxh3(struct sched_db *, int64_t xxh3);
enum sched_rc sched_db_get_by_filename(struct sched_db *, char const *filename);
enum sched_rc sched_db_get_by_hmm_id(struct sched_db *, int64_t hmm_id);

enum sched_rc sched_db_get_all(sched_db_set_func_t, struct sched_db *,
                               void *arg);

enum sched_rc sched_db_add(struct sched_db *, char const *filename);

enum sched_rc sched_db_remove(int64_t id);

/* --- job.h file --- */

typedef void(sched_job_set_func_t)(struct sched_job *, void *arg);

void sched_job_init(struct sched_job *, enum sched_job_type);

enum sched_rc sched_job_get_by_id(struct sched_job *, int64_t id);
enum sched_rc sched_job_get_all(sched_job_set_func_t, struct sched_job *,
                                void *arg);
enum sched_rc sched_job_next_pend(struct sched_job *);

enum sched_rc sched_job_set_run(int64_t id);
enum sched_rc sched_job_set_fail(int64_t id, char const *msg);
enum sched_rc sched_job_set_done(int64_t id);

enum sched_rc sched_job_submit(struct sched_job *, void *actual_job);

enum sched_rc sched_job_increment_progress(int64_t id, int progress);

enum sched_rc sched_job_remove(int64_t id);

/* --- prod.h file --- */

typedef int(sched_prod_write_match_func_t)(FILE *fp, void const *match);
typedef void(sched_prod_set_func_t)(struct sched_prod *, void *arg);

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

/* --- seq.h file --- */

typedef void(sched_seq_set_func_t)(struct sched_seq *, void *arg);

void sched_seq_init(struct sched_seq *seq, int64_t seq_id, int64_t scan_id,
                    char const *name, char const *data);

enum sched_rc sched_seq_get_by_id(struct sched_seq *, int64_t id);
enum sched_rc sched_seq_scan_next(struct sched_seq *);
enum sched_rc sched_seq_get_all(sched_seq_set_func_t fn, struct sched_seq *,
                                void *arg);

/* --- scan.h file --- */

struct sched_prod;
struct sched_seq;

typedef void(sched_scan_set_func_t)(struct sched_scan *, void *arg);

void sched_scan_init(struct sched_scan *, int64_t db_id, bool multi_hits,
                     bool hmmer3_compat);

enum sched_rc sched_scan_get_seqs(int64_t job_id, sched_seq_set_func_t,
                                  struct sched_seq *seq, void *arg);

enum sched_rc sched_scan_get_prods(int64_t job_id, sched_prod_set_func_t,
                                   struct sched_prod *prod, void *arg);

enum sched_rc sched_scan_get_by_id(struct sched_scan *, int64_t scan_id);
enum sched_rc sched_scan_get_by_job_id(struct sched_scan *, int64_t job_id);

void sched_scan_add_seq(char const *name, char const *data);

enum sched_rc sched_scan_get_all(sched_scan_set_func_t, struct sched_scan *,
                                 void *arg);

/* --- error.h file --- */

char const *sched_error_string(enum sched_rc rc);

