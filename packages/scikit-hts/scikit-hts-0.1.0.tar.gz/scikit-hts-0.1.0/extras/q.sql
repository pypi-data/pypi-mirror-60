select ts_ride_start,
       m_duration_sec,
       start_latitude,
       start_longitude,
       end_latitude,
       end_longitude,
       distance_haversine,
       lower(city)    as city,
       lower(country) as country,
       cost_eur
from dwh.fact_rides r
where cost_local >= 0
  and lower(city) in (
    select city
    from (
             select lower(city) as city, count(1) c
             from dwh.fact_rides
             group by lower(city)
             having c > 5000
         ) ct
)
  and lower(city) not in
      (
       'annecy',
       'marseille',
       'cologne',
       'malmo',
       'coimbra',
       'faro',
       'brussels',
       'wallonia',
       'perpignan',
       'sausset & carr'
          )
order by ts_ride_start desc
limit 1000000;


