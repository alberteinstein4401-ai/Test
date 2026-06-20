"""Database operations for querying lesson completion data."""
import mysql.connector
import polars as pl
import psycopg2


def assemble_report_frame(
    postgres_config: dict,
    mysql_config: dict,
    start_date,
    end_date,
) -> pl.DataFrame:
    """Query active users and lesson completions, return aggregated report DataFrame."""
    with psycopg2.connect(**postgres_config) as pg_conn:
        with pg_conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, user_name
                FROM mindtickle_users
                WHERE LOWER(active_status) = 'active'
                """
            )
            active_users_rows = cursor.fetchall()

    if not active_users_rows:
        return pl.DataFrame(
            {
                "Name": [],
                "Number of lessons completed": [],
                "Date": [],
            }
        )

    user_df = pl.DataFrame(
        active_users_rows,
        schema=["user_id", "user_name"],
        orient="row",
    )

    user_ids = user_df["user_id"].to_list()
    if not user_ids:
        return pl.DataFrame(
            {
                "Name": [],
                "Number of lessons completed": [],
                "Date": [],
            }
        )

    placeholders = ",".join(["%s"] * len(user_ids))
    query = f"""
        SELECT completion_id, user_id, lesson_id, completion_date
        FROM lesson_completion
        WHERE completion_date BETWEEN %s AND %s
        AND user_id IN ({placeholders})
    """

    start_date_str = (
        start_date if isinstance(start_date, str) else start_date.isoformat()
    )
    end_date_str = (
        end_date if isinstance(end_date, str) else end_date.isoformat()
    )
    params = [start_date_str, end_date_str, *user_ids]

    with mysql.connector.connect(**mysql_config) as mysql_conn:
        with mysql_conn.cursor() as cursor:
            cursor.execute(query, params)
            lesson_rows = cursor.fetchall()

    if not lesson_rows:
        return pl.DataFrame(
            {
                "Name": [],
                "Number of lessons completed": [],
                "Date": [],
            }
        )

    lessons_df = pl.DataFrame(
        lesson_rows,
        schema=["completion_id", "user_id", "lesson_id", "completion_date"],
        orient="row",
    )

    report_df = (
        lessons_df
        # Keep the latest record if duplicates exist
        .sort("completion_id")
        .unique(
            subset=["user_id", "lesson_id", "completion_date"],
            keep="last",
        )
        .join(user_df, on="user_id", how="inner")
        .group_by(["user_name", "completion_date"])
        .agg(pl.len().alias("Number of lessons completed"))
        .sort(["completion_date", "user_name"])
        .with_columns(
            pl.col("completion_date")
            .cast(pl.Date)
            .dt.strftime("%Y-%m-%d")
            .alias("Date")
        )
        .select(
            [
                pl.col("user_name").alias("Name"),
                "Number of lessons completed",
                "Date",
            ]
        )
    )

    return report_df
