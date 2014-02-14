

#include "ranges.h"
#include <algorithm>


using namespace std;

//
// RangeParser
//
RangeParser::RangeParser()
{}

bool RangeParser::parse(const string& r, ranges_t& result) {
	state = STATE_START;
	ranges_t temp;

	for(string::const_iterator it = r.begin(); it != r.end(); ++it){
		onEvent(*it, temp);
	}
	onEvent(EVENT_EOL, temp);
	if(state != STATE_SUCCESS) 
		return false;

	sort(temp.begin(), temp.end());

	result.clear();
	for(ranges_t::const_iterator it = temp.begin(); it != temp.end(); ++it) {
		range_t range = *it;
		if(range.first >= range.second) 
			return false;

		if(result.size()) {
			range_t& prev_range = result[result.size()-1];
			if(prev_range.second >= range.first)
				prev_range.second = max(prev_range.second, range.second);
			else 
				result.push_back(range);
		} else {
			result.push_back(range);
		}
	}

	return true;
}

void RangeParser::push(const range_value_t v, ranges_t& result) const {
	result.push_back(make_pair(v, v+1));
}
void RangeParser::push(const range_value_t v1, const range_value_t v2, ranges_t& result) const {
	result.push_back(make_pair(v1, v2+1));
}
void RangeParser::push(const string& n, ranges_t& result) const {
	push(atoi(n.c_str()), result);
}
void RangeParser::push(const string& n1, const string& n2, ranges_t& result) const {
	push(atoi(n1.c_str()), atoi(n2.c_str()), result);
}

void RangeParser::onEvent(const int evt, ranges_t& result) {
	switch(state) {
		case STATE_START:
				if(evt >= '0' && evt <= '9') {
					n1 = ""; n2 = "";
					n1 += (char)evt;
					state = STATE_N1;
				} else {
					state = STATE_ERROR;
				}
				break;
		case STATE_N1:
				if(evt >= '0' && evt <= '9') {
					n1 += (char)evt;
				} else if(evt == ',') {
					push(n1, result);
					n1 = "";
				} else if(evt == '-') {
					state = STATE_N2;
				} else if(evt == EVENT_EOL){
					if(n1.length()) 
						push(n1, result);
					state = STATE_SUCCESS;
				} else {
					state = STATE_ERROR;
				}
				break;
		case STATE_N2:
				if(evt >= '0' && evt <= '9') {
					n2 += (char)evt;
				} else if(evt == ',') {
					push(n1, n2, result);
					n1 = ""; n2 = "";
					state = STATE_N1;
				} else if(evt == EVENT_EOL && n2.length()) {
					push(n1, n2, result);
					state = STATE_SUCCESS;
				} else {
					state = STATE_ERROR;
				}
				break;
	}
}




//
// Range
//
Range::Range(const ranges_t& r) : _ranges(r) {
	_size = 0;
	for(ranges_t::const_iterator it = _ranges.begin(); it != _ranges.end(); ++it) {
		_size += it->second - it->first;
	}
}
int Range::size() const {
	return _size;
}
Range::iterator Range::begin() {
	return RangeIterator(*this);
}
Range::iterator Range::end() {
	return RangeIterator(*this, size());
}
Range::iterator Range::random() {
	return RangeIterator(*this, rand() % size());
}




//
// RangeIterator
//


RangeIterator::RangeIterator(Range& range, int offset) : _range(range), _offset(offset){
	_currentRange = range._ranges.begin();

	while((_currentRange->second - _currentRange->first) <= _offset) {
		_offset -= (_currentRange->second - _currentRange->first);
		_currentRange++;
		if(_currentRange == range._ranges.end())
			return;
	}
}
RangeIterator::RangeIterator(const RangeIterator& rhs) : _range(rhs._range), 
                                                         _offset(rhs._offset)
{
	_currentRange = rhs._currentRange;
}

RangeIterator& RangeIterator::operator=(const RangeIterator& rhs) {
	_range = rhs._range;
	_offset = rhs._offset;
	_currentRange = rhs._currentRange;
	return *this;
}

RangeIterator& RangeIterator::operator++() {
	_offset++;
	if((_currentRange->second -  _currentRange->first) <= _offset) {
		_currentRange++;
		_offset = 0;
	}
	return *this;
}
RangeIterator RangeIterator::operator++(int) {
	RangeIterator tmp(*this); 
	operator++(); 
	return tmp;
}
int RangeIterator::operator*() {
	return _currentRange->first + _offset;
}
bool RangeIterator::operator==(const RangeIterator& rhs) {
	return _currentRange == rhs._currentRange && _offset == rhs._offset;
}
bool RangeIterator::operator!=(const RangeIterator& rhs) {
	return !(*this ==rhs);
}
