FROM bitnami/spark:3.1.2


WORKDIR /app


COPY src/spark_Streaming.py /app/

COPY requirements.txt /app

USER root

RUN pip install -r requirements.txt

# Create a directory for Ivy cache and make it writable
RUN mkdir -p /tmp/.ivy2 && chmod 777 /tmp/.ivy2

# Switch back to the non-root user
USER 1001

# Set environment variables for Ivy
ENV IVY_CACHE_DIR=/tmp/.ivy2
ENV IVY_HOME=/tmp/.ivy2

# Set the command to run the Spark job
CMD ["spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,org.apache.spark:spark-avro_2.12:3.1.2", \
     "--conf", "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp/.ivy2 -Divy.home=/tmp/.ivy2", \
     "--conf", "spark.executor.extraJavaOptions=-Divy.cache.dir=/tmp/.ivy2 -Divy.home=/tmp/.ivy2", \
     "--conf", "spark.sql.avro.concatenate=false", \
     "/app/spark_Streaming.py"]