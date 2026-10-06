import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import a_apply
json.dump({str(k): v for k, v in a_apply.F.items()}, open('_a_new.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('dumped %d 题' % len(a_apply.F))
