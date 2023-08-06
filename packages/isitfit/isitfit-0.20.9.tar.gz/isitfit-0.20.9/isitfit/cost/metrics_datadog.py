"""
Manager class for getting datadog data for isitfit

Pre-requisites
    pip3 install datadog asciiplotlib pandas
    apt-get install gnuplot

set env vars
    export DATADOG_API_KEY=...
    export DATADOG_APP_KEY=...
    
Run tests
    pip3 install pytest
    pytest datadogManager.py
"""

import json
import time
import pandas as pd
import os

from isitfit.utils import logger


# Configure the module according to your needs
# Use Datadog REST API client
import datadog

from isitfit.utils import SECONDS_IN_ONE_DAY, DdgNoData, HostNotFoundInDdg, DataNotFoundForHostInDdg


class DataQueryError(ValueError):
  pass


class DatadogApiWrap:
    """
    Assisting the datadog assistant
    """

    def map_aws_datadog(self):
      # Build a map from AWS ID to Datadog hostname
      # FIXME Should probably paginate in pages of 100 hosts using combinations of start and count
      # Leaving for later until this proves to be a problem for isitfit memory consumption during execution.
      # https://docs.datadoghq.com/api/?lang=python#search-hosts
      # https://docs.datadoghq.com/agent/faq/how-datadog-agent-determines-the-hostname/?tab=agentv6v7#potential-host-names
      MAX_COUNT = 1000 # safety net, will cause problems for larger infra
      h_rev = datadog.api.Hosts.search(count=MAX_COUNT)

      if 'status' in h_rev:
        if h_rev['status']=='error':
          msg = "Datadog API/APP keys configured wrong?"
          if 'errors' in h_rev: msg += " Got error: %s"%", ".join(h_rev['errors'])
          from isitfit.cli.click_descendents import IsitfitCliError
          raise IsitfitCliError(msg)

      # alternatively, can use host_name here.
      # Note the similar field used in self.hosts_search below.
      # If this field is changed from name to host_name, remember to change it below also
      h_rev = {x['aws_id']: x['name'] for x in h_rev['host_list'] if 'aws_id' in x and 'name' in x}
      return h_rev


    def hosts_search(self, dd_hostname):
      # https://docs.datadoghq.com/api/?lang=bash#search-hosts
      h_all = datadog.api.Hosts.search(filter='host:%s'%dd_hostname)

      # check if found
      if len(h_all['host_list'])==0:
          raise HostNotFoundInDdg("Did not find datadog hostname %s"%dd_hostname)

      # check if found
      # deprecate above? (of course change condition to != 1)
      if h_all['total_returned']>1:
          raise HostNotFoundInDdg("Found multiple hosts identified by datadog hostname %s"%dd_hostname)

      # filter for the dd_hostname
      # Not enough to take the first because I had a bug where 
      # h_all = api.Hosts.search(host=self.dd_hostname)
      # was returning a list of all hosts because the argument host=... is not supported
      # I'm not sure where I got this usage pattern from, maybe deprecated code.
      # To make matters worse, the datadog api allows the user to pass any parameters 
      # without any checks on their validity: datadog/api/resources.py SearchableAPIResource._search just passes **params to the API
      # WRONG # h_i = h_all['host_list'][0]
      # Alternatively can use host_name, not sure if one is preferred or if one will prove to be buggy
      # Will see how things come out of issue #10
      # https://github.com/autofitcloud/isitfit/issues/10
      # where name was a FQDN instead of an AWS ID
      # For more info, check https://docs.datadoghq.com/agent/faq/how-datadog-agent-determines-the-hostname/?tab=agentv6v7#potential-host-names
      # Note the similar field used in self.map_aws_datadog above.
      # If this field is changed from name to host_name, remember to change it above also
      h_i = [x for x in h_all['host_list'] if x['name']==dd_hostname]

      if len(h_i)==0:
        raise HostNotFoundInDdg("Datadog API usage problem. Hosts.search returns set of hosts, but filtering on instance ID returns an empty set. Applied to host %s in datadog"%dd_hostname)

      # at this stage we can take the first entry
      h_i = h_i[0]

      # 
      gohai = json.loads(h_i['meta']['gohai'])
      memory_total = int(gohai['memory']['total'].replace('kB',''))*1024
      out = {'cpuCores': h_i['meta']['cpuCores'], 'memory_total': memory_total}
      return out


    def metric_query(self, dd_hostname, start, end, query, metric_name, dfcol_name):
      """
      start - number of seconds since unix epoch
      end   - similar
      """
      # convert to seconds since unix epoch
      # https://stackoverflow.com/a/6999787/4126114
      # if start/end were like dt.datetime.now(), then this would be needed
      # but since they're integers to begin with (check DatadogManager.set_ndays, no need for these
      #conv2sec = lambda x: time.mktime(x.timetuple())
      #ue_start = conv2sec(start)
      #ue_end   = conv2sec(end)
      ue_start = start
      ue_end = end

      # query datadog
      # https://docs.datadoghq.com/api/?lang=python#query-timeseries-points
      m = datadog.api.Metric.query(start=ue_start, end=ue_end, query=query)

      if m['status'] != 'ok':
        raise DataQueryError(m['status'])

      if 'errors' in m:
        raise DataQueryError(m['errors'])

      if m['status']!='ok':
        msg1 = m['status']
        msg2 = 'n/a'
        if 'error' in m: msg2 = m['error']
        msg3 = "%s: %s"%(msg1, msg2)
        raise DataQueryError(msg3)

      if len(m['series'])==0:
          raise DataNotFoundForHostInDdg("No %s found for %s"%(metric_name, dd_hostname))

      # filter for the series
      # Instead of just doing
      #    m = m['series'][0]
      # which is not safe (similar to the issue I had with hosts above being a list of other IDs)
      # filter on the metric name
      m = [x for x in m['series'] if x['metric']==metric_name]

      if len(m)==0:
        raise DataNotFoundForHostInDdg("Datadog api usage. Metric query returns set of metrics not corresponding to request. Found for metric=%s and host=%s"%(metric_name, dd_hostname))

      # now safer to filter
      m = m[0]

      # convert to pandas dataframe
      df = pd.DataFrame(m['pointlist'], columns=['ts_int', dfcol_name])
      df['ts_dt'] = pd.to_datetime(df.ts_int, origin='unix', unit='ms')
      del df['ts_int']
      return df


class DatadogAssistant:
    def __init__(self, start, end, dd_hostname):
        self.end = end
        self.start = start
        self.dd_hostname = dd_hostname
        self.apiwrap = DatadogApiWrap()


    def _get_metrics_core(self, query, metric_name, col_i):
        return self.apiwrap.metric_query(dd_hostname=self.dd_hostname, start=self.start, end=self.end, query=query, metric_name=metric_name, dfcol_name=col_i)

    def _get_meta(self):
        return self.apiwrap.hosts_search(self.dd_hostname)
        
    def get_metrics_cpu_max(self):
        # query language
        # https://docs.datadoghq.com/graphing/functions/
        # Use minimum so that cpu_used will be the maximum
        query = 'system.cpu.idle{host:%s}.rollup(min,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'cpu_idle_min'
        metric_name = 'system.cpu.idle'
        df = self._get_metrics_core(query, metric_name, col_i)
        # calculate cpu used as 100 - cpu_idle
        df['cpu_used_max'] = 100 - df.cpu_idle_min
        df['cpu_used_max'] = df['cpu_used_max'].astype(int)
        return df

    def get_metrics_cpu_min(self):
        # query language
        # https://docs.datadoghq.com/graphing/functions/
        # Use minimum so that cpu_used will be the maximum
        query = 'system.cpu.idle{host:%s}.rollup(max,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'cpu_idle_max'
        metric_name = 'system.cpu.idle'
        df = self._get_metrics_core(query, metric_name, col_i)
        # calculate cpu used as 100 - cpu_idle
        df['cpu_used_min'] = 100 - df.cpu_idle_max
        df['cpu_used_min'] = df['cpu_used_min'].astype(int)
        return df
        
    def get_metrics_cpu_avg(self):
        # repeat for average
        query = 'system.cpu.idle{host:%s}.rollup(avg,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'cpu_idle_avg'
        metric_name = 'system.cpu.idle'
        df = self._get_metrics_core(query, metric_name, col_i)
        df['cpu_used_avg'] = 100 - df.cpu_idle_avg
        df['cpu_used_avg'] = df['cpu_used_avg'].astype(int)
        return df

    def get_metrics_ram_max(self):
        # query language, check note above in get_metrics_cpu
        query = 'system.mem.free{host:%s}.rollup(min,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'ram_free_min'
        metric_name = 'system.mem.free'
        df =  self._get_metrics_core(query, metric_name, col_i)
        memory_total = self._get_meta()['memory_total']
        df['ram_free_min'] = df.ram_free_min / memory_total * 100
        df['ram_free_min'] = df['ram_free_min'].astype(int)
        df['ram_used_max'] = 100 - df['ram_free_min']
        return df

    def get_metrics_ram_min(self):
        # query language, check note above in get_metrics_cpu
        query = 'system.mem.free{host:%s}.rollup(max,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'ram_free_max'
        metric_name = 'system.mem.free'
        df =  self._get_metrics_core(query, metric_name, col_i)
        memory_total = self._get_meta()['memory_total']
        df['ram_free_max'] = df.ram_free_max / memory_total * 100
        df['ram_free_max'] = df['ram_free_max'].astype(int)
        df['ram_used_min'] = 100 - df['ram_free_max']
        return df

    def get_metrics_ram_avg(self):
        # query language, check note above in get_metrics_cpu
        query = 'system.mem.free{host:%s}.rollup(avg,%i)'%(self.dd_hostname, SECONDS_IN_ONE_DAY)
        col_i = 'ram_free_avg'
        metric_name = 'system.mem.free'
        df =  self._get_metrics_core(query, metric_name, col_i)
        memory_total = self._get_meta()['memory_total']
        df['ram_free_avg'] = df.ram_free_avg / memory_total * 100
        df['ram_free_avg'] = df['ram_free_avg'].astype(int)
        df['ram_used_avg'] = 100 - df['ram_free_avg']
        return df

    def get_metrics_count(self):
        # query language, check note above in get_metrics_cpu
        query = 'count_not_null(system.mem.free{host:%s})'%(self.dd_hostname)
        col_i = 'nhours'
        metric_name = 'count_not_null(system.mem.free)'
        df1 =  self._get_metrics_core(query, metric_name, col_i)
        # yields data per hour, so process in pandas to daily
        df2 = df1.set_index('ts_dt').resample('1D').nhours.sum().reset_index()
        return df2


class DatadogManager:
    def __init__(self):
        datadog.initialize()
        self.set_ndays(90) # default is 90 days
        self.print_configured = True
        self.map_aws_dd = None


    def set_ndays(self, ndays):
        self.ndays = ndays
        self.end = int(time.time())
        
        # datadog will automatically set the resolution based on the start-end range
        # if the ".rollup" is not used in the query
        # number of seconds in 1 hour, if no ".rollup" specified in query, this yields 20-second frequency from datadog
        # n_secs = 60*60
        # number of seconds in 90 days, if no ".rollup" specified in query, yields bi-daily from datadog
        n_secs = SECONDS_IN_ONE_DAY*self.ndays
        self.start = self.end - n_secs


    def is_configured(self):
      from isitfit.utils import ping_matomo

      # check not None and not empty string
      if os.getenv('DATADOG_API_KEY', None):
        if os.getenv('DATADOG_APP_KEY', None):
          if self.print_configured:
            logger.info("Datadog env vars available")
            ping_matomo("/cost/setting?datadog.is_configured=True")
            self.print_configured = False
          return True
          
      if self.print_configured:
        logger.info("Datadog env vars missing. Set DATADOG_API_KEY and DATADOG_APP_KEY to get memory data from Datadog.")
        ping_matomo("/cost/setting?datadog.is_configured=False")

        import click
        display_msg = lambda x: click.secho(x, fg='yellow')
        display_msg("Note: without the datadog integration, memory metrics are missing, thus only CPU is used, which is not representative for memory-bound applications.")
        display_msg("If you gather memory metrics using another provider than datadog, please get in touch at https://www.autofitcloud.com/contact")
        self.print_configured = False

      return False


    def build_map_aws_dd(self):
        apiwrap = DatadogApiWrap()
        self.map_aws_dd = apiwrap.map_aws_datadog()


    def get_metrics_all(self, aws_id):
        # convert aws ID to datadog hostname
        if self.map_aws_dd is None:
          self.build_map_aws_dd()
          if self.map_aws_dd is None:
            raise Exception("Failed to build aws-datadog ID map")

        # fail if not found
        if aws_id not in self.map_aws_dd:
          raise HostNotFoundInDdg("Did not find host aws ID %s in datadog reverse map"%aws_id)

        dd_hostname = self.map_aws_dd[aws_id]

        # FIXME: we already have cpu from cloudwatch, so maybe just focus on ram from datadog
        logger.debug("Fetching datadog data for aws ID %s, datadog hostname %s"%(aws_id, dd_hostname))
        ddgL2 = DatadogAssistant(self.start, self.end, dd_hostname)
        df_cpu_max = ddgL2.get_metrics_cpu_max()
        df_cpu_min = ddgL2.get_metrics_cpu_min()
        df_cpu_avg = ddgL2.get_metrics_cpu_avg()
        df_ram_max = ddgL2.get_metrics_ram_max()
        df_ram_min = ddgL2.get_metrics_ram_min()
        df_ram_avg = ddgL2.get_metrics_ram_avg()
        df_count   = ddgL2.get_metrics_count()
        df_all = (
            df_cpu_max
            .merge(df_cpu_min, how='outer', on=['ts_dt'])
            .merge(df_cpu_avg, how='outer', on=['ts_dt'])
            .merge(df_ram_max, how='outer', on=['ts_dt'])
            .merge(df_ram_min, how='outer', on=['ts_dt'])
            .merge(df_ram_avg, how='outer', on=['ts_dt'])
            .merge(df_count,   how='outer', on=['ts_dt'])
        )
        df_all = df_all[['ts_dt', 'cpu_used_max', 'cpu_used_min', 'cpu_used_avg', 'ram_used_max', 'ram_used_min', 'ram_used_avg', 'nhours']]

        # convert from datetime to date to be able to merge with cloudtrail
        df_all['ts_dt'] = df_all.ts_dt.dt.date

        # rename like cloudwatch
        df_all.rename(columns={'ts_dt': 'Timestamp'}, inplace=True)

        return df_all


from .cacheManager import MetricCacheMixin


class DatadogCached(MetricCacheMixin, DatadogManager):
    def get_key(self, aws_id):
        cache_key = "datadog:cpu+ram:%s:%i"%(aws_id, self.ndays)
        return cache_key

    def get_metrics_base(self, rc_describe_entry, rc_id, rc_created):
      return self.get_metrics_all(rc_id)


#class DatadogListener(DatadogCached):
#    """
#    A listener for the Event Bus defined in mainManager.py
#    """
#    def per_ec2(self, context_ec2):
#        raise Exception("Deprecated")
#
#        if not self.is_configured():
#          context_ec2['ddg_df'] = None
#          return context_ec2
#
#        # parse out keys
#        # FIXME build/use map from AWS EC2 instance ID to Datadog hostname
#        dd_hostname = context_ec2['ec2_obj'].instance_id
#
#        # get data
#        ddg_df = self.get_metrics_all(dd_hostname)
#
#        if ddg_df is None:
#          context_ec2['ddg_df'] = None
#          return context_ec2
#
#        # add to context
#        context_ec2['ec2_df'] = ec2_df # update context
#        context_ec2['ddg_df'] = ddg_df
#
#        # return
#        return context_ec2
#
