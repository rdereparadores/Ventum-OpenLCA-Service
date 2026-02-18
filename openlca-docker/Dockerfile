FROM maven:3.9.12-eclipse-temurin-21 AS mvn
WORKDIR /olca-ipc
COPY pom.xml .
RUN mvn package

FROM eclipse-temurin:21-jre
COPY --from=mvn /olca-ipc/target/lib /app/lib
COPY run.sh /app
RUN chmod +x /app/run.sh
ENTRYPOINT [ "/app/run.sh" ]