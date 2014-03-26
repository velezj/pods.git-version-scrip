
#include <string>
#include <boost/property_tree/ptree.hpp>
#include <boost/exception/all.hpp>



namespace git_version {


  // Description:
  // The response from git_version_script (raw)
  typedef boost::error_info<struct git_version_script_raw_response_tag, std::string > git_version_script_raw_response_error_info;


  // Description:
  // Returns a boost::property_tree::ptree structure with the git version
  // of the code in the given directory.
  boost::property_tree::ptree
  git_version( const std::string& root );
  


}
