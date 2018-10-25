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

#ifndef __PIXELINKTYPES_H_4EEC0224_1E0B_48d0_96D6_95858CE25D6E
#define __PIXELINKTYPES_H_4EEC0224_1E0B_48d0_96D6_95858CE25D6E

// Extended types
typedef ULONG	U32, *PU32;
typedef USHORT	U16, *PU16;
typedef UCHAR	U8, *PU8;

typedef LONG	S32, *PS32;
typedef SHORT	S16, *PS16;
typedef CHAR	S8, *PS8;

typedef float F32, *PF32;

// Return codes
typedef int PXL_RETURN_CODE;

// Video Clip File Format
#define CLIP_FORMAT_AVI     0

// Feature IDs
#define FEATURE_BRIGHTNESS	            0
#define FEATURE_EXPOSURE	            1
#define FEATURE_SHARPNESS	            2
#define FEATURE_WHITE_BAL	            3
#define FEATURE_HUE	                    4
#define FEATURE_SATURATION	            5
#define FEATURE_GAMMA	                6
#define FEATURE_SHUTTER		            7
#define FEATURE_GAIN	                8
#define FEATURE_IRIS	                9
#define FEATURE_FOCUS	                10
#define FEATURE_TEMPERATURE	            11
#define FEATURE_TRIGGER	                12
#define FEATURE_ZOOM	                13
#define FEATURE_PAN	                    14
#define FEATURE_TILT	                15
#define FEATURE_OPT_FILTER	            16
#define FEATURE_GPIO                    17
#define FEATURE_FRAME_RATE              18
#define FEATURE_ROI                     19
#define FEATURE_FLIP                    20
#define FEATURE_DECIMATION              21
#define FEATURE_PIXEL_FORMAT            22
#define FEATURE_EXTENDED_SHUTTER        23
#define FEATURE_AUTO_ROI                24
#define FEATURE_LOOKUP_TABLE            25
#define FEATURE_MEMORY_CHANNEL          26

#define FEATURES_TOTAL                  27

// For PxLGetCameraFeatures
#define FEATURE_ALL 0xFFFFFFFF

// Feature Flags
#define FEATURE_FLAG_PRESENCE       0x00000001
#define FEATURE_FLAG_MANUAL         0x00000002
#define FEATURE_FLAG_AUTO           0x00000004
#define FEATURE_FLAG_ONEPUSH        0x00000008
#define FEATURE_FLAG_OFF            0x00000010
#define FEATURE_FLAG_DESC_SUPPORTED 0x00000020
#define FEATURE_FLAG_READ_ONLY      0x00000040

// Image File Format
#define IMAGE_FORMAT_BMP        0
#define IMAGE_FORMAT_TIFF       1
#define IMAGE_FORMAT_PSD        2
#define IMAGE_FORMAT_JPEG       3


// Pixel Format
#define PIXEL_FORMAT_MONO8      0
#define PIXEL_FORMAT_MONO16     1
#define PIXEL_FORMAT_YUV422     2
#define PIXEL_FORMAT_BAYER8     3
#define PIXEL_FORMAT_BAYER16    4
#define PIXEL_FORMAT_RGB24      5
#define PIXEL_FORMAT_RGB48      6

// Preview State
#define START_PREVIEW   0
#define PAUSE_PREVIEW   1
#define STOP_PREVIEW    2

// Stream State
#define START_STREAM    0
#define PAUSE_STREAM    1
#define STOP_STREAM     2

// Trigger types
#define TRIGGER_TYPE_FREE_RUNNING         0
#define TRIGGER_TYPE_SOFTWARE             1
#define TRIGGER_TYPE_HARDWARE             2

// Descriptors
#define PXL_MAX_STROBES         16
#define PXL_MAX_KNEE_POINTS     4

// Descriptors (advanced features)
#define PXL_UPDATE_CAMERA 0
#define PXL_UPDATE_HOST   1

// Default Memory Channel
#define FACTORY_DEFAULTS_MEMORY_CHANNEL	0


// Camera Features
typedef struct _FEATURE_PARAM
{
    float fMinValue;
    float fMaxValue;
} FEATURE_PARAM, *PFEATURE_PARAM;

typedef struct _CAMERA_FEATURE
{
    U32 uFeatureId;
    U32 uFlags;
    U32 uNumberOfParameters;
    FEATURE_PARAM *pParams;
} CAMERA_FEATURE, *PCAMERA_FEATURE; 

typedef struct _CAMERA_FEATURES
{
    U32 uSize;
    U32 uNumberOfFeatures;
    CAMERA_FEATURE *pFeatures;
}  CAMERA_FEATURES, *PCAMERA_FEATURES;


// Camera Info
typedef struct _CAMERA_INFO
{
	S8 VendorName [33];
	S8 ModelName [33];
	S8 Description [256];
	S8 SerialNumber[33];
	S8 FirmwareVersion[12];
	S8 FPGAVersion[12];
	S8 CameraName[256];
} CAMERA_INFO, *PCAMERA_INFO;

// Frame Descriptor
typedef struct _FRAME_DESC
{
    U32 uSize;
    float fFrameTime;
    U32 uFrameNumber;

    struct _Brightness{
        float fValue;
    } Brightness;

    struct{
        float fValue;
    } AutoExposure;

    struct{
        float fValue;
    } Sharpness;

    struct{
        float fValue;
    } WhiteBalance;

    struct{
        float fValue;
    } Hue;

    struct{
        float fValue;
    } Saturation;

    struct{
        float fValue;
    } Gamma;

    struct{
        float fValue;
    } Shutter;

    struct{
        float fValue;
    } Gain;

    struct{
        float fValue;
    } Iris;

    struct{
        float fValue;
    } Focus;

    struct{
        float fValue;
    } Temperature;

    struct{
        float fMode;
        float fType;
        float fPolarity;
        float fDelay;
        float fParameter;
    } Trigger;

    struct{
        float fValue;
    } Zoom;

    struct{
        float fValue;
    } Pan;

    struct{
        float fValue;
    } Tilt;

    struct{
        float fValue;
    } OpticalFilter;

    struct{
        float fMode[PXL_MAX_STROBES];
        float fPolarity[PXL_MAX_STROBES];
        float fParameter1[PXL_MAX_STROBES];
        float fParameter2[PXL_MAX_STROBES];
        float fParameter3[PXL_MAX_STROBES];
    } GPIO;

    struct{
        float fValue;
    } FrameRate;

    struct{
        float fLeft;
        float fTop;
        float fWidth;
        float fHeight;
    } Roi;

    struct{
        float fHorizontal;
        float fVertical;
    } Flip;

    struct{
    float fValue;
    } Decimation;

    struct{
        float fValue;
    } PixelFormat;

    struct{
        float fKneePoint[PXL_MAX_KNEE_POINTS];
    } ExtendedShutter;

    struct{
        float fLeft;
        float fTop;
        float fWidth;
        float fHeight;
    } AutoROI;

} FRAME_DESC, *PFRAME_DESC;

typedef struct _ERROR_REPORT
{
	PXL_RETURN_CODE uReturnCode;
	S8 strFunctionName[32];
	S8 strReturnCode[32];
	S8 strReport[256];
} ERROR_REPORT, *PERROR_REPORT;

// Overlay usage
#define OVERLAY_PREVIEW      0x01
#define OVERLAY_FORMAT_IMAGE 0x02
#define OVERLAY_FORMAT_CLIP  0x04
#define OVERLAY_FRAME        0x08

#endif //__PIXELINKTYPES_H_4EEC0224-1E0B-48d0-96D6-95858CE25D6E
