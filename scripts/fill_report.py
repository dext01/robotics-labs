#!/usr/bin/env python3
"""Write evidence/prNN/report.json.

  python3 scripts/fill_report.py PR05 --commit <impl-sha> \
      --true public_tests_passed defect_reproduced defect_fixed replay_verified

Only mark a claim true after you have checked it yourself.
"""
import argparse
import json
import subprocess
from pathlib import Path

CLAIMS = {
    'PR05': ['public_tests_passed', 'defect_reproduced', 'defect_fixed', 'replay_verified'],
    'PR06': ['public_tests_passed', 'defect_reproduced', 'defect_fixed'],
    'PR07': ['public_tests_passed', 'defect_reproduced', 'defect_fixed', 'headless_verified',
             'recording_verified', 'odometry_tf_owned'],
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('practice', choices=sorted(CLAIMS))
    p.add_argument('--commit', default='HEAD', help='SHA of the implementation commit')
    p.add_argument('--ai-used', choices=['true', 'false'], default='true')
    p.add_argument('--true', nargs='*', default=[], metavar='CLAIM')
    a = p.parse_args()
    unknown = set(a.true) - set(CLAIMS[a.practice])
    if unknown:
        p.error(f'unknown claims for {a.practice}: {sorted(unknown)}')
    sha = subprocess.check_output(['git', 'rev-parse', a.commit], text=True).strip()
    report = {'practice': a.practice, 'commit': sha, 'ai_used': a.ai_used == 'true'}
    report.update({c: c in a.true for c in CLAIMS[a.practice]})
    out = Path('evidence') / a.practice.lower() / 'report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(out.read_text())


if __name__ == '__main__':
    main()
