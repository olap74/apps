#!/bin/bash

LOGFILE='data_with_logs.txt'

echo "Project,Folder,Owners,Last Log Date,Last Log Data"
echo "Project,Folder,Owners,Last Log Date,Last Log Data" > $LOGFILE

for i in $(gcloud projects list --format="value(projectId)" | grep -v sys-)
do 
  PARENT=$(gcloud projects describe $i --format="value(parent.id)")
  OWNERS=$(gcloud projects get-iam-policy $i --flatten="bindings[].members" --filter="bindings.role=roles/owner" --format="value(bindings.members)")
  LOGGING=$(gcloud services list --enabled --project $i | grep logging)
  BILLING_ENABLED=$(gcloud billing projects describe $i --format="value(billingEnabled)")
  BILLING_ACCOUNT=$(gcloud billing projects describe $i --format="value(billingAccountName)")

  if [ -z "$LOGGING" ]
  then
    LASTLOG="None"
    LASTLOGDATE="None"
  else
    LASTLOG=$(gcloud logging read "" --project=$i --freshness=3y --limit=1 --format="value(protoPayload.methodName)")
    LASTLOGDATE=$(gcloud logging read "" --project=$i --freshness=3y --limit=1 --format="value(receiveTimestamp)")
  fi

  OWNER=$(echo "$OWNERS" | tr '\n' ' ')

  echo "$i,$PARENT,$OWNER,$LASTLOGDATE,$LASTLOG,$BILLING_ENABLED,$BILLING_ACCOUNT"
  echo "$i,$PARENT,$OWNER,$LASTLOGDATE,$LASTLOG,$BILLING_ENABLED,$BILLING_ACCOUNT" >> $LOGFILE

done
