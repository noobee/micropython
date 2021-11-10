
// *************************************************************************
// *                                                                       *
// *    MicroPython 'hid' module                                           *
// *                                                                       *
// *************************************************************************

#define PRODUCT "HID Interface"
#define PACKAGE "hid"
#define PROGRAM "modhid.c"
#define VERSION "0.00"
#define CHANGES "0000"
#define TOUCHED "2021-09-07 00:00:00"
#define LICENSE "MIT Licensed"
#define DETAILS "https://opensource.org/licenses/MIT"

// .--------------------------------------------------------------------------.
// |    MIT Licence                                                           |
// `--------------------------------------------------------------------------'

// Copyright 2021, "Hippy"

// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.

// .-----------------------------------------------------------------------.
// |    MicroPython, Pico C SDK and TinyUSB includes                       |
// `-----------------------------------------------------------------------'

#include "py/runtime.h"
#include "py/objstr.h"

#include "pico/stdlib.h"
#include "tusb.h"

// .-----------------------------------------------------------------------.
// |    Set Binary Information to show added module                        |
// `-----------------------------------------------------------------------'

#include "pico/binary_info.h"

#ifndef BI_AM_ADD
#define BI_AM_TAG               BINARY_INFO_MAKE_TAG('A', 'M')
#define BI_AM_ID                0x61F52DA4
#define BI_AM_ADD(nam)          bi_decl(bi_string(BI_AM_TAG, BI_AM_ID, nam))

bi_decl(bi_program_feature_group_with_flags(
        BI_AM_TAG, BI_AM_ID, "added modules",
        BI_NAMED_GROUP_SEPARATE_COMMAS | BI_NAMED_GROUP_SORT_ALPHA));
#endif

BI_AM_ADD("_hid")

// *************************************************************************
// *                                                                       *
// *    Hook into tusb_genusb_hid.c                                        *
// *                                                                       *
// *************************************************************************

extern void GenUsb_Hid_SendKeyboardReport(uint8_t modifier, uint8_t keycode);

extern void GenUsb_Hid_SendMouseReport(int8_t up, uint8_t left);

// *************************************************************************
// *                                                                       *
// *    MicroPython interface                                              *
// *                                                                       *
// *************************************************************************

STATIC const MP_DEFINE_STR_OBJ(PRODUCT_string_obj, PRODUCT);
STATIC const MP_DEFINE_STR_OBJ(PACKAGE_string_obj, PACKAGE);
STATIC const MP_DEFINE_STR_OBJ(PROGRAM_string_obj, PROGRAM);
STATIC const MP_DEFINE_STR_OBJ(VERSION_string_obj, VERSION);
STATIC const MP_DEFINE_STR_OBJ(CHANGES_string_obj, CHANGES);
STATIC const MP_DEFINE_STR_OBJ(TOUCHED_string_obj, TOUCHED);
STATIC const MP_DEFINE_STR_OBJ(LICENSE_string_obj, LICENSE);
STATIC const MP_DEFINE_STR_OBJ(DETAILS_string_obj, DETAILS);

STATIC mp_obj_t hid_keypress(mp_obj_t modifier_obj, mp_obj_t keycode_obj) {
  int modifier = mp_obj_get_int(modifier_obj);
  int keycode  = mp_obj_get_int(keycode_obj);
  GenUsb_Hid_SendKeyboardReport(modifier, keycode);
  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(hid_keypress_obj, hid_keypress);

STATIC mp_obj_t hid_move(mp_obj_t up_obj, mp_obj_t right_obj) {
  int up   = mp_obj_get_int(up_obj);
  int right = mp_obj_get_int(right_obj);
  GenUsb_Hid_SendMouseReport(up, right);
  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(hid_move_obj, hid_move);

// *************************************************************************
// *                                                                       *
// *    MicroPython module definition                                      *
// *                                                                       *
// *************************************************************************

STATIC const mp_rom_map_elem_t hid_module_globals_table[] = {
  { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR__hid)       },

  { MP_ROM_QSTR(MP_QSTR_PRODUCT),  MP_ROM_PTR(&PRODUCT_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_PACKAGE),  MP_ROM_PTR(&PACKAGE_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_PROGRAM),  MP_ROM_PTR(&PROGRAM_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_VERSION),  MP_ROM_PTR(&VERSION_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_CHANGES),  MP_ROM_PTR(&CHANGES_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_TOUCHED),  MP_ROM_PTR(&TOUCHED_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_LICENSE),  MP_ROM_PTR(&LICENSE_string_obj) },
  { MP_ROM_QSTR(MP_QSTR_DETAILS),  MP_ROM_PTR(&DETAILS_string_obj) },

  { MP_ROM_QSTR(MP_QSTR_keypress), MP_ROM_PTR(&hid_keypress_obj)   },
  { MP_ROM_QSTR(MP_QSTR_move),     MP_ROM_PTR(&hid_move_obj)       },

};
STATIC MP_DEFINE_CONST_DICT(hid_module_globals, hid_module_globals_table);

// .-----------------------------------------------------------------------.
// |    MicroPython integration                                            |
// `-----------------------------------------------------------------------'

const mp_obj_module_t mp_module_hid = {
  .base = { &mp_type_module },
  .globals = (mp_obj_dict_t *)&hid_module_globals,
};

// *************************************************************************
// *                                                                       *
// *    End of 'hid' module                                                *
// *                                                                       *
// *************************************************************************
