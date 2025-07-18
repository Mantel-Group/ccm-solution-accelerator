import csv
from jinja2 import Environment, FileSystemLoader

def readCSV(file):
    with open(file, 'rt',encoding='utf-8') as q:
        lines = q.read().split("\n")
        return list(csv.DictReader(lines))

def render_jinja(data,template,output):
    template_dir = '.'
    env = Environment(loader=FileSystemLoader(template_dir)).get_template(template)
    result = env.render(data = data)
    print(f"Writing {output}")
    with open(output,'wt',encoding='utf-8') as q:
        q.write(result)

def main(metrics,framework):

    fw = readCSV(framework)
    data = readCSV(metrics)
    for x in data:
        x['slo_limit'] = float(x['slo_limit'])
        x['slo_target'] = float(x['slo_target'])
        x['references'] = []

        for f in x['framework'].split(';'):
            found = False
            for ff in fw:
                if ff['id'] == f:
                    found = True
                    x['references'].append(ff)
            if not found:
                print(f"ERROR : could not find {f} for {x['metric_id']}")
    render_jinja(data,'template_metrics.md','../docs/metric_library.md')

main('seeds/seed__metric_library.csv','seeds/seed__metric_framework.csv')