package ro.pub.cs.vmchecker.client.i18n;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.Constants;

public interface UploadConstants extends Constants {

	String teamMsg();

	String md5sumInvalid();
	String md5sumIncomplete();

	String loadMd5sum();
	String loadMd5sumFail();
	String loadStorageDir();
	String loadStorageDirFail();

	String uploadFile();
	String uploadFileSuccess();
	String uploadFileFail();

	String uploadMd5();
	String uploadMd5Success();
	String uploadMd5Fail();

	String evaluate();
	String evaluateSuccess();
	String evaluateFailMd5();
	String evaluateFailZip();

	String uploadNormalHeader();
	String uploadNormalFooter();
	String uploadFileButton();

	String uploadLargeHeader();
	String uploadLargeFooter();
	String uploadMd5Button();
	String evaluationButton();
	String md5Title();
	String md5SumEmpty();
	String md5SumTimeComment();
	String md5SumOldDesc();
	String md5SumDesc();
	String archiveTitle();
	String archiveDesc();
	String fileListEmpty();

}
