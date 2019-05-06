import sys

from jbase.replace import Replace

spr_range = range(3924, 3943)
blend_range = range(19)

item = Replace(src='ground_barren.blend',
               frames={key: val for (key, val) in zip(spr_range, blend_range)}
               )
