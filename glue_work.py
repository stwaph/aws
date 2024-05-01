Gaming Analytics: Use AWS Glue and Amazon Redshift Spectrum to Join Game Operational and Data Warehouse Data



Introduction

Game developers and business analysts often need to perform ad-hoc queries and generate reports by joining data from disparate sources, such as transactional databases and data warehouses. In the fast-paced game development cycle, minimizing development effort and optimizing costs are crucial considerations. Operational data specific to a game, such as player metrics, chat room usage, or leaderboard rankings, is typically stored separately from analytical data, like sessions played, payment amounts, and time spent in-game, which is often housed in a data warehouse.

When ad-hoc reporting requirements arise and long-term persistence of joined data is unnecessary, Amazon Redshift Spectrum presents an ideal solution for combining operational and analytical data. If reports need to be generated periodically over time—hours, days, or weeks—AWS Glue can automate the process by providing connectors to data sources, built-in Apache Spark environments for data transformations, and workflow orchestration capabilities.

This blog post demonstrates how to leverage AWS Glue to extract and transform data from an Amazon Relational Database Service (RDS) instance and seamlessly integrate it with data stored in an Amazon Redshift cluster using Amazon Redshift Spectrum. We'll use an example scenario of finding players in chat rooms with the highest numbers of seconds played and highest payment amounts.

Prerequisites and Setup

For the game transactional data source, we’ll use a player table in Amazon RDS MySQL.  The player entity represents the player with id, community, created and updated attributes in addition to other attributes.  

On the data warehouse side, we’ll define a player statistics table with player id, total seconds played, total session count , total payment count and total payment amount attributes.

With data sources defined, to join operational data with data warehouse data, we’ll need to extract the operational data from RDS MySQL, drop unnecessary columns and write the output to Amazon S3 in compressed (snappy) parquet format.  With the requirement to run reports over time, we’ll partition the data in Amazon S3 by date to enhance query performance and optimize query costs.


With prerequisites completed and data stores defined, let’s go back to requirements: extract operational data from Amazon RDS Aurora MySQL, transform by dropping unnecessary columns and write (load) in date format partitions to Amazon S3 for query by Amazon Redshift Spectrum.  The extract, transform, load operation also needs to be repeatable for reports over time.  As AWS Glue has built-in Apache Spark and Python environments for performing transform operations, uses connectors for data sources and has workflow orchestration for automation, we will need connectors, crawlers, jobs and a workflow to prepare data for joining with Amazon Redshift tables.

Glue → Crawlers → Create Crawler

Select JDBC connection created previously, Data Source is MySQL database name/table (% wildcard allowed), GlueServiceRole created in prerequisite step and a ‘database’ name which is a schema in the Glue Catalog.  The database name should reflect the purpose of the Glue data catalog entry.
 
Create a second crawler for crawling the data written to s3 by the Glue Job that combines tables and transforms columns.  This crawler updates the Glue data catalog with the new combined schema.



  Glue Jobs

Two Glue jobs will be used transform the MySQL table by dropping redundant columns, write the table in compressed parquet to s3 and generate a timestamp parameter that will be used by the partitioning job.

<insert code block with combine_player_tables job here>

<insert code block with add_spectrum_table_partition job here>
TODO, refactor JDBC connection block to use secrets manager instead of hardcoded creds

Glue Workflows for Orchestration

Now to pull crawlers and jobs together with AWS Glue workflow orchestration by creating a workflow (scheduled or on-demand) and dragging and dropping crawlers, triggers and jobs in execution order.
                                                                                                                                                              
                                                                                                                                                              Each crawler and job should be tested independently to verify successful connections and function.

Before running the players_db_to_datawarehouse workflow, create an external table and external schema for Amazon Redshift Spectrum.  The table and columns should mirror the schema for the table created by the AWS Glue transform_player_table job.

The external schema command requires a schema name, a data catalog name (we’ll use the default ‘dev’ database), region and the ‘mySpectrumRole’ we created in the prerequisite steps.

“create external table” will reference the external schema name, create a new table name, add columns matching the AWS Glue transform_player_table job columns (and data types), define a partition schema, identify Amazon S3 bucket location, object format and compression type.


For the last Amazon Redshift Spectrum step, grant usage on the external schema to required users.

With the Amazon Redshift Spectrum external table and schema created, the AWS Glue workflow tested and ready, we can trigger the workflow and query the resulting data set using Amazon Redshift Query Editor v2.

Select all available partitions:

Select all rows from a specific partition:
Select all rows joining the Amazon Redshift provisioned cluster table and the Amazon Redshift Spectrum external table for a specific partition:
With data available from both data sources and the ability to join Amazon Redshift provisioned cluster tables and Amazon Redshift Spectrum external tables, let’s query to find players with the highest number seconds played:

Lastly, the players with the highest payment amounts:

Conclusion

AWS data analytics services provide flexible and cost-optimized solutions for combining data from various sources and performing ad-hoc queries and analysis. Amazon Redshift Spectrum enables querying data in Amazon S3 data lakes, either standalone or joined with data from Amazon Redshift clusters or serverless workgroups, offering a low-cost approach for game developers and analysts.

AWS Glue simplifies the process of building and maintaining data pipelines to support these analytics workloads. Its Apache Spark environments, connectors, and workflow orchestration capabilities automate the extract, transform, and load (ETL) processes, minimizing development effort and operational overhead.

The fast-paced gaming industry demands performant, adaptable, and cost-effective solutions for transforming and analyzing data from disparate sources to gain insights and enhance player experiences. The integration of Amazon Redshift Spectrum and AWS Glue addresses these needs, allowing efficient data analysis and informed decision-making.

