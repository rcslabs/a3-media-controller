#ifndef __RANGES_H__
#define __RANGES_H__


#include <string>
#include <utility>
#include <vector>



typedef unsigned int range_value_t;
typedef std::pair<range_value_t, range_value_t> range_t;
typedef std::vector<range_t> ranges_t;


class RangeParser {
public:
	RangeParser();
	bool parse(const std::string& r, ranges_t& result);

private:
	static const int STATE_START   = 0;
	static const int STATE_N1      = 1;
	static const int STATE_N2      = 2;
	static const int STATE_SUCCESS = 3;
	static const int STATE_ERROR   = 4;

	static const int EVENT_EOL = -1;

	int    state;
	std::string n1;
	std::string n2;

	void push(const range_value_t v, ranges_t& result) const;
	void push(const range_value_t v1, const range_value_t v2, ranges_t& result) const;
	void push(const std::string& n, ranges_t& result) const;
	void push(const std::string& n1, const std::string& n2, ranges_t& result) const;

	void onEvent(const int evt, ranges_t& result);
};




class Range;


class RangeIterator {
public:
	RangeIterator(Range& range, int offset = 0);
	RangeIterator(const RangeIterator&);

	RangeIterator& operator++();
	RangeIterator operator++(int);
	int operator*();
	RangeIterator& operator=(const RangeIterator&);
	bool operator==(const RangeIterator& rhs);
	bool operator!=(const RangeIterator& rhs);

private:
	Range&             _range;
	ranges_t::iterator _currentRange;
	unsigned int       _offset;

	RangeIterator();
};



class Range {
public:
	Range(const ranges_t& r);


	int size() const;

	typedef RangeIterator iterator;

	iterator begin();
	iterator end();
	iterator random();

private:
	Range();
	Range(const Range&);

	friend class RangeIterator;
	int      _size;
	ranges_t _ranges;
};



#endif
