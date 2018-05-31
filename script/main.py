import sys

from yuweol_raw import Raw
from dumper import dumper
from analyzer import Analyzer

RESULT_DIR="result"

def test1(r1, r2):
	size_x = 20
	size_y = 20

	a1 = Analyzer(r1)
	a2 = Analyzer(r2)
	
	a1.normalize_burst_touch(1)
	a2.normalize_burst_touch(1)
	
	a1.set_region_label(size_x, size_y)
	a2.set_region_label(size_x, size_y)
	
	d = dumper(RESULT_DIR)
	d.prepare_region(a1, size_x, size_y, "bot")
	
	td1 = dumper(RESULT_DIR)
	td1.prepare_region_distance(a1, size_x, size_y, "bot")
	
	td2 = dumper(RESULT_DIR)
	td2.prepare_region_direction(a1, size_x, size_y, "bot")
	
	td3 = dumper(RESULT_DIR)
	td3.prepare_region(a2, size_x, size_y, "human")
	
	td4 = dumper(RESULT_DIR)
	td4.prepare_region_distance(a2, size_x, size_y, "human")
	
	td5 = dumper(RESULT_DIR)
	td5.prepare_region_direction(a2, size_x, size_y, "human")
	
	d.merge(td1)
	d.merge(td2)
	d.merge(td3)
	d.merge(td4)
	d.merge(td5)
	d.write("region")
	
def main():
	if not len(sys.argv) is 3:
		print ("[usage] python log.py ${log_file} ${log_file}")
		sys.exit(1)
		
	r1 = Raw(sys.argv[1])
	r2 = Raw(sys.argv[2])
	
	test1(r1, r2)
	
if __name__ == "__main__":
	main()
	
#LEFT0 RIGHT8000 UP0 DOWN8000
