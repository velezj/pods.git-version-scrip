
#include "git_version.hpp"
#include <pstream/pstream.h>
#include <sstream>
#include <boost/property_tree/json_parser.hpp>


namespace git_version {

  boost::property_tree::ptree
  git_version( const std::string& root ) {
    
    // creat the command to run, using pod-run
    // to localize to current pod
    std::ostringstream cmd;
    cmd << "pod-run git-version-script " << root;
    
    // run the command in an external process
    redi::ipstream in( cmd.str().c_str() );
    
    // read the command output into a buffer
    std::string line;
    std::ostringstream buffer;
    while( std::getline( in, line ) ) {
      buffer << line << std::endl;
    }

    // parse the output as JSON into a ptree
    boost::property_tree::ptree res;
    try {
      std::istringstream iss( buffer.str() );
      boost::property_tree::json_parser::read_json( iss, res );
    } catch( boost::exception& e ) {
      // something happener here, rethrow
      e << git_version_script_raw_response_error_info( buffer.str() );
      throw;
    }
    
    // return the parsed output
    return res;
  }


}
