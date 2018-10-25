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
#ifndef __PIXELINKAPI_H_68C66B9E_76EC_4290_9983_6A68B7698290
#define __PIXELINKAPI_H_68C66B9E_76EC_4290_9983_6A68B7698290

#ifdef PIXELINKAPI_EXPORTS
#define PXL_API __declspec(dllexport) __stdcall
#else
#define PXL_API __declspec(dllimport) __stdcall 
#endif

#include "PixelinkTypes.h"
#include "PixelinkCodes.h"

extern "C"
{
PXL_RETURN_CODE
PXL_API
PxLFormatClip( 
        IN LPSTR pInputFileName,
        IN LPSTR pOutputFileName,
        IN U32 uOutputFormat);

PXL_RETURN_CODE 
PXL_API
PxLFormatImage( 
        IN LPVOID pSrc,
        IN PFRAME_DESC pFrameDesc,
        IN U32 uOutputFormat,
        OUT LPVOID pDest,
        IN OUT PU32 pDestBufferSize);

PXL_RETURN_CODE
PXL_API
PxLGetCameraFeatures( 
        IN HANDLE hCamera,
        IN U32 uFeatureId,
        OUT PCAMERA_FEATURES pFeatureInfo,
        IN OUT PU32 pBufferSize);

PXL_RETURN_CODE 
PXL_API
PxLGetCameraInfo( 
        IN HANDLE hCamera,
        OUT PCAMERA_INFO pInformation);

PXL_RETURN_CODE 
PXL_API
PxLGetClip( 
        IN HANDLE hCamera,
        IN U32 uNumberOfFrames,
        IN LPSTR pFileName, 
        IN U32 (_stdcall * TerminationFunction)(
        IN HANDLE hCamera,
        IN U32 uNumberOfFramesCaptured,
        IN PXL_RETURN_CODE uRetCode));

PXL_RETURN_CODE 
PXL_API
PxLGetErrorReport(
        IN HANDLE hCamera,
        OUT PERROR_REPORT pErrorReport);

PXL_RETURN_CODE 
PXL_API
PxLGetFeature( 
        IN HANDLE hCamera,
        IN U32 uFeatureId,
        OUT PU32 pFlags,
        IN OUT PU32 pNumberParms,
        OUT PF32 pParms);

PXL_RETURN_CODE 
PXL_API
PxLGetNextFrame( 
        IN HANDLE hCamera,
        IN U32 uBufferSize,
        OUT LPVOID pFrame,
        OUT PFRAME_DESC pDescriptor);

PXL_RETURN_CODE 
PXL_API
PxLGetNumberCameras(
        OUT PU32 pSerialNumbers,
        IN OUT PU32 pNumberSerial);

PXL_RETURN_CODE 
PXL_API
PxLInitialize( 
        IN U32 uSerialNumber,
        OUT HANDLE* phCamera);

PXL_RETURN_CODE 
PXL_API
PxLResetPreviewWindow( 
        IN HANDLE hCamera);

PXL_RETURN_CODE 
PXL_API
PxLSetCallback ( 
        IN HANDLE hCamera,
        IN U32 uOverlayUse,
        IN LPVOID pContext,
        IN U32 (_stdcall * DataProcessFunction)(
                IN HANDLE hCamera,
                IN OUT LPVOID pFrameData,
                IN U32 uDataFormat, 
                IN PFRAME_DESC pDescriptor,
                IN LPVOID pContext));

PXL_RETURN_CODE 
PXL_API
PxLSetCameraName(
        IN HANDLE hCamera,
        IN LPSTR pCameraName);

PXL_RETURN_CODE 
PXL_API
PxLSetFeature(
        IN HANDLE hCamera,
        IN U32 uFeatureId,
        IN U32 uFlags,
        IN U32 uNumberParms,
        IN PF32 pParms);

PXL_RETURN_CODE 
PXL_API
PxLSetPreviewSettings(
        IN HANDLE hCamera,
        IN LPSTR pTitle="PixeLINK Preview",
        IN U32 uStyle=
        WS_OVERLAPPEDWINDOW|WS_VISIBLE,
        IN U32 uLeft=CW_USEDEFAULT, 
        IN U32 uTop=CW_USEDEFAULT,
        IN U32 uWidth=CW_USEDEFAULT,
        IN U32 uHeight=CW_USEDEFAULT,
        IN HWND hParent=NULL,
        IN U32 uChildId=0);

PXL_RETURN_CODE 
PXL_API
PxLSetPreviewState(
        IN HANDLE hCamera,
        IN U32 uPreviewState,
        OUT HWND *pHWnd);

PXL_RETURN_CODE 
PXL_API
PxLSetStreamState(
        IN HANDLE hCamera,
        IN U32 uStreamState);

PXL_RETURN_CODE 
PXL_API
PxLUninitialize(
        IN HANDLE hCamera);

PXL_RETURN_CODE 
PXL_API
PxLCreateDescriptor( 
        IN HANDLE hCamera,
        OUT HANDLE * pDescriptorHandle,
        IN U32 uUpdateMode);

PXL_RETURN_CODE 
PXL_API
PxLRemoveDescriptor( 
        IN HANDLE hCamera,
        IN HANDLE hDescriptor);

PXL_RETURN_CODE 
PXL_API
PxLUpdateDescriptor(
        IN HANDLE hCamera,
        IN HANDLE hDescriptor,
        IN U32 uUpdateMode);

PXL_RETURN_CODE 
PXL_API
PxLSaveSettings(
        IN HANDLE hCamera,
        IN U32 uChannel);

PXL_RETURN_CODE 
PXL_API
PxLLoadSettings(
        IN HANDLE hCamera,
        IN U32 uChannel);

} // end extern "C"
#endif // __PIXELINKAPI_H_68C66B9E_76EC_4290_9983_6A68B7698290
