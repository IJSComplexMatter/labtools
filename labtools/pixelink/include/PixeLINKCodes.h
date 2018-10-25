/****************************************************************************************************************
 * COPYRIGHT © 2002 PixeLINK CORPORATION.  ALL RIGHTS RESERVED.                                                 *
 *                                                                                                              *
 * Copyright Notice and Disclaimer of Liability:                                                                *
 *                                                                                                              *
 *                                                                                                              *
 * PixeLINK Corporation is henceforth referred to as PixeLINK or PixeLINK Corporation.                          *
 * Purchaser henceforth refers to the original purchaser(s) of the equipment, and/or any legitimate user(s).    *
 *                                                                                                              *
 * PixeLINK hereby explicitly prohibits any form of reproduction (with the express strict exception for backup  *
 * and archival purposes, which are allowed as stipulated within the License Agreement for PixeLINK Corporation *
 * Software), modification, and/or distribution of this software and/or its associated documentation unless     *
 * explicitly specified in a written agreement signed by both parties.                                          *
 *                                                                                                              *
 * To the extent permitted by law, PixeLINK disclaims all other warranties or conditions of any kind, either    *
 * express or implied, including but not limited to all warranties or conditions of merchantability and         *
 * fitness for a particular purpose and those arising by statute or otherwise in law or from a course of        *
 * dealing or usage of trade. Other written or oral statements by PixeLINK, its representatives, or others do   *
 * not constitute warranties or conditions of PixeLINK.                                                         *
 *                                                                                                              *
 * PixeLINK makes no guarantees or representations, including but not limited to: the use of, or the result(s)  *
 * of the use of: the software and associated documentation in terms of correctness, accuracy, reliability,     *
 * being current, or otherwise. The Purchaser hereby agree to rely on the software, associated hardware and     *
 * documentation and results stemming from the use thereof solely at their own risk.                            *
 *                                                                                                              *
 * By using the products(s) associated with the software, and/or the software, the Purchaser and/or user(s)     *
 * agree(s) to abide by the terms and conditions set forth within this document, as well as, respectively,      *
 * any and all other documents issued by PixeLINK in relation to the product(s).                                *
 *                                                                                                              *
 * PixeLINK is hereby absolved of any and all liability to the Purchaser, and/or a third party, financial or    *
 * otherwise, arising from any subsequent loss, direct and indirect, and damage, direct and indirect,           *
 * resulting from intended and/or unintended usage of its software, product(s) and documentation, as well       *
 * as additional service(s) rendered by PixeLINK, such as technical support, unless otherwise explicitly        *
 * specified in a written agreement signed by both parties. Under no circumstances shall the terms and          *
 * conditions of such an agreement apply retroactively.                                                         *
 *                                                                                                              *
 ****************************************************************************************************************/

#ifndef __PIXELINKCODES_H_8473FA7C_A76B_42bd_9BB3_3832639286FD
#define __PIXELINKCODES_H_8473FA7C_A76B_42bd_9BB3_3832639286FD
 
#define ApiSuccess	                0x00000000	// The function completed successfully
#define ApiUnknownError	            0x80000001	// Unknown error
#define ApiInvalidHandleError	    0x80000002	// The handle parameter invalid
#define ApiInvalidParameterError	0x80000003	// Invalid parameter
#define ApiBufferTooSmall	        0x80000004	// A buffer passed as parameter is too small.
#define ApiInvalidFunctionCallError	0x80000005	// The function cannot be called at this time 
#define ApiNotSupportedError	    0x80000006	// The API cannot complete the request
#define ApiCameraInUseError	        0x80000007	// The camera is already being used by another application
#define ApiNoCameraError	        0x80000008	// There is no response from the camera
#define ApiHardwareError	        0x80000009	// The Camera responded with an error
#define ApiCameraUnknownError	    0x8000000A	// The API does not recognize the camera
#define ApiOutOfBandwidthError	    0x8000000B	// There is not enough 1394 bandwidth to start the stream
#define ApiOutOfMemoryError	        0x8000000C	// The API can not allocate the required memory
#define ApiOSVersionError	        0x8000000D	// The API cannot run on the current operating system
#define ApiNoSerialNumberError		0x8000000E	// The serial number coundn't be obtained from the camera
#define ApiInvalidSerialNumberError 0x8000000F	// A camera with that serial number coundn't be found
#define ApiDiskFullError            0x80000010  // Not enough disk space to complete an IO operation
#define ApiIOError                  0x80000011  // An error occurred during an IO operation
#define ApiStreamStopped            0x80000012  // Application requested streaming termination
#define ApiNullPointerError		    0x80000013	// The pointer parameter=NULL
#define ApiCreatePreviewWndError	0x80000014	// Error creating the preview window
#define	ApiSuccessParametersChanged 0x00000015  // Indicates that a set feature is successful but one or more parameter had to be changed (ROI)
#define ApiOutOfRangeError          0x80000016  // Indicates that a feature set value is out of range 
#define ApiNoCameraAvailableError   0x80000017	// There is no camera available
#define ApiInvalidCameraName        0x80000018  // Indicated that the name specified is not a valid camera name
#define ApiGetNextFrameBusy         0x80000019  // GextNextFrame() can't be called at this time because its being use by an FRAME_OVERLAY callback function
#define ApiSuccessAlreadyRunning    0x0000001A  // The stream is already started

#define ApiStreamExistingError      0x90000001  
#define ApiEnumDoneError            0x90000002   
#define ApiNotEnoughResourcesError  0x90000003
#define ApiBadFrameSizeError        0x90000004
#define ApiNoStreamError            0x90000005
#define ApiVersionError             0x90000006 
#define ApiNoDeviceError            0x90000007
#define ApiCannotMapFrameError      0x90000008
#define ApiOhciDriverError          0x90000009
#define ApiInvalidIoctlParameter    0x90000010 // The input or output buffer size is not valid


#endif //__PIXELINKCODES_H_8473FA7C_A76B_42bd_9BB3_3832639286FD
