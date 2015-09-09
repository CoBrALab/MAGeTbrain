#include <minc2.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <volume_io.h>
#include <bicpl.h>
#include <ParseArgv.h>
#include <time_stamp.h>
#include <bicpl.h>

/* argument parsing defaults */
static int verbose = FALSE;
static int clobber = FALSE;

/* argument table */
static ArgvInfo argTable[] = {
   {NULL, ARGV_HELP, (char *)NULL, (char *)NULL,
    "General options:"},
   {"-verbose", ARGV_CONSTANT, (char *)TRUE, (char *)&verbose,
    "print out extra information"},
   {"-clobber", ARGV_CONSTANT, (char *)TRUE, (char *)&clobber,
    "clobber existing files"},
   {NULL, ARGV_HELP, (char *)NULL, (char *)NULL, ""},
   {NULL, ARGV_END, NULL, NULL, NULL}
};

int main(int argc, char **argv){

  char               *src_obj_file, *out_obj_file;
  polygons_struct    *polygons;
  Point              *points;
  Vector             *normals;
  File_formats        format;
  object_struct     **objects;
  int                 n_objects;

  if(argc != 3){
    fprintf(stderr, "Usage: %s  input.obj output.obj\n", argv[0]);
    return (1);

  }


  initialize_argument_processing(argc, argv);
  src_obj_file  = argv[1];
  out_obj_file  = argv[2];

  if (input_graphics_file(src_obj_file,
                          &format, &n_objects, &objects ) != OK ) {
        return( 1 );
  }

  if( n_objects != 1 || get_object_type(objects[0]) != POLYGONS ) {
        fprintf(stderr, "File must contain exactly 1 polygons struct.\n" );
        return( 1 );
  }

  polygons = get_polygons_ptr(objects[0]);
  // n_points = get_object_points(objects[0], &points);




  compute_polygon_normals(polygons);

   if( (output_graphics_file( out_obj_file, ASCII_FORMAT, 1, &objects[0] )) \
!= OK)
   {
     printf("Cannot output %s\n", out_obj_file);
     return(1);
   }

   output_graphics_file( out_obj_file, ASCII_FORMAT, 1, &objects[0] );
   return(0);


}
