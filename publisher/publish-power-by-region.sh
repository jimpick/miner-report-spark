#! /bin/bash

set -e
set +x

TMP=$WORK_DIR/tmp
mkdir -p $TMP

./setup-textile.sh

IFS="$(printf '\n\t')"
DATE=$(node -e 'console.log((new Date()).toISOString())')

TARGET=$WORK_DIR/dist/miner-power-daily-average-latest
if [ ! -d $TARGET ]; then
	mkdir -p $TARGET
	cd $TARGET
	hub bucket init \
		--thread $TEXTILE_BUCKET_THREAD \
		--key $BUCKET_MINER_POWER_DAILY_AVERAGE_LATEST_KEY
fi


if [ -f $OUTPUT_POWER_REGIONS_DIR/sum_avg_daily/json/_SUCCESS ] ; then
  PART=$(ls $OUTPUT_POWER_REGIONS_DIR/sum_avg_daily/json/part*.json | head -1)

  cat $PART | jq -s "{ \
    date: \"$DATE\", \
    rows: .
  }" > $TMP/miner-power-by-region.json

fi

if [ -f $OUTPUT_POWER_SYNTHETIC_REGIONS_DIR/sum_avg_daily/json/_SUCCESS ] ; then
  PART=$(ls $OUTPUT_POWER_SYNTHETIC_REGIONS_DIR/sum_avg_daily/json/part*.json | head -1)

  cat $PART | jq -s "{ \
    date: \"$DATE\", \
    rows: .
  }" > $TMP/provider-power-by-synthetic-region.json
fi

cd $TARGET
hub bucket pull -y

mv $TMP/miner-power-by-region.json .
echo miner-power-by-region.json:
head miner-power-by-region.json

mv $TMP/provider-power-by-synthetic-region.json .
echo provider-power-by-synthetic-region.json:
head provider-power-by-synthetic-region.json

hub bucket push -y

