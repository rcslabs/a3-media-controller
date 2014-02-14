#include "cl.h"
#include "log.h"

//#include <getopt.h>
//#include <string>


/*bool Cl::parse(int argc, char *argv[]) {
	confidentiality  = false;
	authentication   = false;
	in               = "";
	out              = "";
	key              = "";
	ssrc             = 0;


	char * in_s     = NULL;
	char * out_s    = NULL;
	char * key_s    = NULL;
	char * ssrc_s   = NULL;

	static struct option long_options[] = {
		{"in",   1,  0,    0},
		{"out",  1,  0,    0},
		{"key",  1,  0,    0},
		{"ssrc", 1,  0,    0},
		{NULL,   0,  NULL, 0}
	};

	int option_index = 0;


	while (1) {
		int c = getopt_long(argc, argv, "ae", long_options, &option_index);
		if (c == -1) {
			break;
		}

		//int this_option_optind = optind ? optind : 1;
		switch (c) {
		case 0:
			if(option_index == 0) {               // IN=
				in_s = optarg;
			} else if(option_index == 1) {        // OUT=
				out_s = optarg;
			} else if(option_index == 2) {        // KEY=
				key_s = optarg;
			} else if(option_index == 3) {        // SSRC=
				ssrc_s = optarg;
			}
			break;
		case 'e':
			confidentiality = true;
			break;
		case 'a':
			authentication = true;
			break;
		default:
			log(LOG_INFO, "Unknown param in command line");
			return false;
		}
	}

	if(!(in_s && out_s && key_s && ssrc_s)) {
		if(!in_s)   log(LOG_INFO, "<in> not specified");
		if(!out_s)  log(LOG_INFO, "<out> not specified");
		if(!key_s)  log(LOG_INFO, "<key> not specified");
		if(!ssrc_s) log(LOG_INFO, "<ssrc> not specified");
		return false;
	}

	in   = in_s;
	out  = out_s;
	key  = key_s;
	ssrc = atoll(ssrc_s);

	if(!ssrc) {
		log(LOG_INFO, "ssrc is not a valid number");
		return false;
	}

	//if ((sec_servs && !input_key) || (!sec_servs && input_key)) {
	//	// 
	//	// a key must be provided if and only if security services have
	//	// been requested 
	//	// 
	//	printf("a key must be provided if and only if security services have");
	//	usage(argv[0]);
	//}
	return true;
}
*/

/*

void Cl::help(const std::string& programName) const {
	printf("usage: %s --key=<key> --ssrc=<ssrc> --in=<address:port> --out=<address:port> [-a][-e] "
	       "where  -a use message authentication\n"
	       "       -e use encryption\n"
	       "       --key=<key>  sets the srtp master key\n"
	       "       --ssrc=<ssrc> sets SSRC\n"
	       "       --in=<address:port> receives rtp on udp port\n"
	       "       --out=<address:port> send srtp on address port\n",
	       programName.c_str());
}

*/
